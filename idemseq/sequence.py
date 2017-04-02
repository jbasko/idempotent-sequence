import logging

from idemseq.base import Options
from idemseq.command import Command


log = logging.getLogger(__name__)


class SequenceCommand(object):
    """
    Represents state of Command execution as part of a Sequence.
    """

    status_unknown = 'unknown'
    status_failed = 'failed'
    status_finished = 'finished'

    valid_statuses = (
        status_unknown,
        status_failed,
        status_finished,
    )

    class AlreadyCompleted(Exception):
        pass

    class PreviousStepsNotFinished(Exception):
        pass

    def __init__(self, command, sequence=None):
        super(SequenceCommand, self).__init__()
        self._command = command
        self._sequence = sequence

    def __getattr__(self, item):
        return getattr(self._command, item)

    def __setattr__(self, key, value):
        if key in ('_command', '_sequence'):
            return super(SequenceCommand, self).__setattr__(key, value)
        else:
            return setattr(self._command, key, value)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self._command == other._command
            and self._sequence == other._sequence
        )

    @property
    def command(self):
        return self._command

    def reset(self):
        self._sequence.state_registry.update_status(self, self.status_unknown)

    @property
    def is_finished(self):
        return self._sequence.state_registry.get_status(self) == self.status_finished

    def run(self):
        """
        Checks if this sequence command is ready to be run and if so -- runs it.
        Otherwise raises an explanatory exception.
        """

        if self._sequence.is_finished and not self.options.run_always:
            raise self.AlreadyCompleted(self.name)

        if self.is_finished and not (self.options.run_always or self.options.run_until_finished):
            raise self.AlreadyCompleted(self.name)

        # Go through previous steps and make sure they are all finished
        if not self._sequence.is_all_finished_before(self):
            raise self.PreviousStepsNotFinished()

        kwargs = {}
        for param in self._command.parameters:
            if param.name in self._sequence.context:
                kwargs[param.name] = self._sequence.context[param.name]

        result = self._command(**kwargs)
        self._sequence.state_registry.update_status(self, self.status_finished)

        return result

    def __str__(self):
        return '{}(name={})'.format(self.__class__.__name__, self.name)


class SequenceBase(object):
    def __init__(self, *commands, **seq_options):
        self._order = {}
        self._commands = {}

        for c in commands or ():
            if not isinstance(c, Command):
                c = Command(func=c)

            # When passing commands to SequenceBase constructor, it is assumed
            # that the commands are supplied in the order in which they should
            # run. This means that any custom order option on individual commands
            # will be ignored:
            assert c.options.order == -1

            self._register_command(c)

    def __len__(self):
        return len(self._commands)

    def __contains__(self, item):
        return item in self._commands

    def __getitem__(self, item):
        return self._commands[item]

    def __iter__(self):
        for name in sorted(self._order, key=self._order.get):
            yield self._commands[name]

    def __call__(self, step_registry_name=None):
        return Sequence(state_registry_name=step_registry_name, base=self)

    def index_of(self, command_name):
        assert command_name in self
        for i, name in enumerate(sorted(self._order, key=self._order.get)):
            if name == command_name:
                return i

    def _register_command(self, command, order=None):
        if command.name in self._commands:
            raise ValueError(command.name)
        self._commands[command.name] = command
        self._order[command.name] = order or len(self._order)

    def command(self, f=None, **options):
        def decorator(func):
            command = Command(func=func, **options)
            self._register_command(command, order=options.get('order'))
            return command

        if f:
            return decorator(f)
        else:
            return decorator


class SequenceRunOptions(Options):
    _valid_options = {
        'warn_only': False,
    }



class Sequence(object):
    """
    Sequence is a concrete instance of SequenceBase.

    An sequence state may be run multiple times.
    """
    state_registry_cls = None

    def __init__(self, base, state_registry_name=None):
        self._sequence_base = base

        # Context cannot be injected in constructor, should be supplied at run attempt time.
        self._context = None

        state_registry_cls = self.state_registry_cls
        if state_registry_cls is None:
            from idemseq.persistence import SqliteStateRegistry
            state_registry_cls = SqliteStateRegistry
        self._state_registry = state_registry_cls(name=state_registry_name)

    def __iter__(self):
        for command in self._sequence_base:
            yield SequenceCommand(command=command, sequence=self)

    def __contains__(self, item):
        return item in self._sequence_base

    def __getitem__(self, item):
        if item not in self._sequence_base:
            raise KeyError(item)
        return SequenceCommand(command=self._sequence_base[item], sequence=self)

    def __len__(self):
        return len(self._sequence_base)

    @property
    def context(self):
        return self._context

    def reset(self):
        for command in self._sequence_base:
            self.state_registry.update_status(command, SequenceCommand.status_unknown)

    @property
    def state_registry(self):
        return self._state_registry

    @property
    def is_finished(self):
        return all(command_state.is_finished for command_state in self)

    def is_all_finished_before(self, step):
        known_statuses = self.state_registry.get_known_statuses()
        for s in self:
            if step == s:
                return True
            if s.name not in known_statuses or known_statuses[s.name] != SequenceCommand.status_finished:
                return False
        return False

    def run(self, context=None, **run_options):
        """
        Runs the sequence of steps.
        """
        options = SequenceRunOptions(run_options)

        self._context = context or {}

        if self.is_finished:
            run_always = [command for command in self if command.options.run_always]
            if not run_always:
                log.info('Nothing to do, all commands in sequence already finished')
                return

            for command in run_always:
                try:
                    command.run()
                except Exception as e:
                    if options.warn_only:
                        log.warning(e)
                        return
                    raise
            return

        for step in self:
            try:
                step.run()
            except SequenceCommand.AlreadyCompleted:
                continue
            except Exception as e:
                if options.warn_only:
                    log.warning(e)
                    return
                raise
