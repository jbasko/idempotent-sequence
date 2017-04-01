import inspect

from idemseq.invocation import CommandSequenceInvocation


class CommandOptions(dict):
    _valid_options = {
        'name': None,
        'order': -1,
        'run_always': None,
    }

    def __getattr__(self, item):
        if item in self._valid_options:
            return self.get(item, self._valid_options[item])
        else:
            raise AttributeError(item)


class Command(object):
    """
    Represents a function that is run as part of a sequence.
    
    Commands aren't meant to be executed directly because they have no
    knowledge of the context in which they are called 
    (whether they have called before, whether other commands have been completed etc.).
    
    Instead, create and run a Step which encapsulates all the invocation information of a Command.
    """
    def __init__(self, func=None, **options):
        self._func = func

        self._options = CommandOptions(options)

        self._signature = None
        if self._func:
            self._signature = inspect.signature(self._func)

    @property
    def name(self):
        return self.options.name or self._func.__name__

    @property
    def parameters(self):
        """
        Returns a view of parameters from underlying function's signature.
        """
        return self._signature.parameters.values()

    @property
    def options(self):
        """
        Options passed to the Command decorator/constructor.
        """
        return self._options

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


class CommandSequence(object):
    def __init__(self, *commands, **seq_options):
        self._commands = {}

        for c in commands or ():
            if isinstance(c, Command):
                self._register_command(c)
            else:
                self._register_command(Command(func=c))

    def _register_command(self, command):
        if command.name in self._commands:
            raise ValueError(command.name)
        self._commands[command.name] = command

    @property
    def commands(self):
        return self._commands

    def command(self, f=None, **options):
        def decorator(func):
            options.setdefault('order', len(self._commands) + 1)  # The default order is the order of declaration
            command = Command(func=func, **options)
            self._register_command(command)
            return command

        if f:
            return decorator(f)
        else:
            return decorator

    def __iter__(self):
        for command in sorted(self._commands.values(), key=lambda c: c.options.order):
            yield command

    def __call__(self, step_registry_name=None, context=None):
        return CommandSequenceInvocation(step_registry_name=step_registry_name, sequence=self, context=context)

    def run_without_registration(self, context=None):
        """
        Runs the commands of this sequence, but it uses in-memory storage
        :param context: 
        :return: 
        """
        self(':memory:', context=context).run()
