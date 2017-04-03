import logging

import collections

import functools
import uuid

from werkzeug.local import LocalStack, LocalProxy

from idemseq.base import Options, AttrDict, DryRunResult
from idemseq.command import Command
from idemseq.exceptions import PreviousStepsNotFinished

log = logging.getLogger(__name__)


class SequenceRunOptions(Options):
    _valid_options = {
        'warn_only': False,
        'dry_run': None,
        'start_at': None,
        'stop_before': None,
    }


_sequence_env_stacks = collections.defaultdict(LocalStack)


def get_current_sequence_env(sequence_uid):
    env = _sequence_env_stacks[sequence_uid].top
    if env is None:
        raise RuntimeError('Requesting current sequence environment outside of context')
    return env


class SequenceEnv(object):
    def __init__(self, sequence_uid=None, context=None, **run_options):
        self.sequence_uid = sequence_uid
        self.context = AttrDict(context or {})
        self.run_options = SequenceRunOptions(run_options)

    def push(self):
        top = _sequence_env_stacks[self.sequence_uid].top
        if top:
            self.context.set_parent(top.context)
            self.run_options.set_parent(top.run_options)
        _sequence_env_stacks[self.sequence_uid].push(self)

    def pop(self):
        popped = _sequence_env_stacks[self.sequence_uid].pop()
        if popped is not self:
            raise RuntimeError('Popped wrong {}'.format(self.__class__.__name__))
        self.context.set_parent(None)
        self.run_options.set_parent(None)

    def __enter__(self):
        self.push()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()


class SequenceCommand(object):
    """
    Represents state of Command execution as part of a Sequence.
    
    This object should have no local state because user is allowed to create any number of these
    to represent the same thing. All writes should go to either self._command, or self._sequence.
    """

    status_unknown = 'unknown'
    status_failed = 'failed'
    status_finished = 'finished'

    valid_statuses = (
        status_unknown,
        status_failed,
        status_finished,
    )

    def __init__(self, command, sequence=None):
        super(SequenceCommand, self).__init__()
        self._command = command
        self._sequence = sequence

    def __getattr__(self, item):
        return getattr(self._command, item)

    def __setattr__(self, key, value):
        if key in ('_command', '_sequence', 'status'):
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

    @property
    def status(self):
        return self._sequence.get_command_status(self)

    @status.setter
    def status(self, status):
        self._sequence.set_command_status(self, status)

    def reset(self):
        self.status = self.status_unknown

    @property
    def is_finished(self):
        return self.status == self.status_finished

    def run(self):
        """
        Low-level method to run individual commands.
        """
        try:
            if self._sequence.is_finished and not self.options.run_always:
                log.debug('Command "{}" already completed - skipping'.format(self.name))
                return

            if self.is_finished and not (self.options.run_always or self.options.run_until_finished):
                log.debug('Command "{}" already completed - skipping'.format(self.name))
                return

            # Make sure previous steps are all finished
            if not self._sequence.is_all_finished_before(self):
                raise PreviousStepsNotFinished()

            kwargs = {}
            for param in self._command.parameters:
                if param.name in self._sequence.context:
                    kwargs[param.name] = getattr(self._sequence.context, param.name)

            if self._sequence.run_options.dry_run:
                log.info('[dry-run] Command "{}"'.format(self.name))
                result = DryRunResult(command=self._command, kwargs=kwargs)
            else:
                result = self._command(**kwargs)

            self.status = self.status_finished

            return result

        except Exception as e:
            if self._sequence.run_options.warn_only:
                log.warning('[warn-only] Command "{}" failed:'.format(self.name))
                log.exception(e)
            else:
                raise

    def __str__(self):
        return '{}(name={})'.format(self.__class__.__name__, self.name)

    def __repr__(self):
        return '<{}>'.format(self)


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

    def __call__(self, step_registry_name=None, context=None, **run_options):
        return Sequence(state_registry_name=step_registry_name, base=self, context=context, **run_options)

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


class Sequence(object):
    """
    Sequence is a concrete instance of SequenceBase.

    An sequence state may be run multiple times.
    """
    state_registry_cls = None

    def __init__(self, base, state_registry_name=None, context=None, **run_options):
        self._base = base
        self._uid = uuid.uuid4()
        self._current_env = LocalProxy(functools.partial(get_current_sequence_env, self.uid))

        state_registry_cls = self.state_registry_cls
        if state_registry_cls is None:
            from idemseq.persistence import SqliteStateRegistry
            state_registry_cls = SqliteStateRegistry
        self._real_state_registry = state_registry_cls(name=state_registry_name)
        self._dry_run_state_registry_instance = None

        # This is a dirty hack to ensure that we aren't building on top of another, unrelated sequence env stack
        try:
            assert self.run_options
            raise Exception('Should have raised RuntimeError, the env stack is not clean')
        except RuntimeError:
            # Expected
            pass

        # Initialise this sequence's environment stack with whatever was passed at instantiation time
        self.env(context=context, **run_options).push()

    @property
    def uid(self):
        """
        Unique identifier of the sequence instance to ensure that it has its own Sequence environment stack.
        """
        return self._uid

    def __iter__(self):
        """
        Returns an iterator over all sequence commands.
        
        This is the recommended way of processing commands to run/inspect because this applies
        some run_options that aren't applied by accessing commands directly.
        """

        start_at = self.run_options.start_at
        if start_at and start_at not in self:
            raise ValueError('Invalid command specified for run option start_at - "{}"'.format(start_at))

        stop_before = self.run_options.stop_before
        if stop_before and stop_before not in self:
            raise ValueError('Invalid command specified for run option stop_before - "{}"'.format(stop_before))

        for command in self._base:
            if start_at:
                if command.name != start_at:
                    continue
                else:
                    start_at = None

            if stop_before and command.name == stop_before:
                return

            yield SequenceCommand(command=command, sequence=self)

    @property
    def commands(self):
        """
        A generator for v2 that always yields the next command that can run, or stops the iteration if it can't.
        This isn't implemented yet.
        """
        # TODO [v2]
        raise NotImplementedError()
        for command in self:
            yield command

    @property
    def all_commands(self):
        """
        A generator that yields all commands irrespective of `run_options` and command completion status.
        """
        for command in self._base:
            yield SequenceCommand(command=command, sequence=self)

    def __contains__(self, item):
        return item in self._base

    def __getitem__(self, item):
        if item not in self._base:
            raise KeyError(item)
        return SequenceCommand(command=self._base[item], sequence=self)

    def __len__(self):
        return len(self._base)

    def __str__(self):
        return '<{} ({})>'.format(self.__class__.__name__, ', '.join(str(c.name) for c in self._base))

    def env(self, context=None, **run_options):
        return SequenceEnv(sequence_uid=self.uid, context=context, **run_options)

    @property
    def context(self):
        return self._current_env.context

    @property
    def run_options(self):
        return self._current_env.run_options

    def reset(self):
        log.warning('Resetting state')
        for command in self.all_commands:
            command.reset()

    @property
    def _dry_run_state_registry(self):
        """
        Lazily loaded private property because we don't want to be copying real state unless required to.
        During a normal run which does not consult _dry_run_state_registry, this isn't initialised.
        If it has been initialised during a normal run, its state is maintained by duplicating
        all calls to the real state registry in `set_command_status`.
        """
        if self._dry_run_state_registry_instance is None:
            from idemseq.persistence import DryRunStateRegistry
            self._dry_run_state_registry_instance = DryRunStateRegistry(name=self._real_state_registry.name)

            # During initialisation, we have to copy the entire state so that in case dry_run context
            # is entered, we return the right state.
            for k, v in self._real_state_registry.get_known_statuses().items():
                if k in self._base:
                    self._dry_run_state_registry_instance.update_status(self[k], v)

        return self._dry_run_state_registry_instance

    @property
    def _state_registry(self):
        """
        This is a private property, to get command status, use `get_command_status`
        """
        if self.run_options.dry_run:
            return self._dry_run_state_registry
        else:
            return self._real_state_registry

    @property
    def is_finished(self):
        return all(command.is_finished for command in self.all_commands)

    def is_all_finished_before(self, step):
        known_statuses = self._state_registry.get_known_statuses()
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
        with self.env(context=context, **run_options):
            if self.is_finished:
                run_always = [command for command in self if command.options.run_always]
                if run_always:
                    log.debug('Sequence has already been completed, running commands marked with run_always')
                    for command in run_always:
                        command.run()
                else:
                    log.info('Nothing to do, all commands in sequence already finished')
            else:
                for command in self:
                    command.run()

    def set_command_status(self, sequence_command, status):
        assert sequence_command._sequence is self
        if not self.run_options.dry_run:
            self._real_state_registry.update_status(sequence_command, status)
        self._dry_run_state_registry.update_status(sequence_command, status)

    def get_command_status(self, sequence_command):
        assert sequence_command._sequence is self
        return self._state_registry.get_status(sequence_command)
