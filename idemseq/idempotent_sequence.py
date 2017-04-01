import inspect

from idemseq.invocation import Step
from idemseq.persistence import SqliteStepRegistry


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


class IdempotentSequence(object):
    step_registry_cls = SqliteStepRegistry

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

    def _get_commands_in_order(self):
        for command in sorted(self._commands.values(), key=lambda c: c.options.order):
            yield command

    def generate_steps(self, context=None):
        """
        Generate steps one by one.
        """
        context = context or {}
        for index, command in enumerate(self._get_commands_in_order()):
            yield Step(index=index, command=command, context=context)

    def run(self, context=None):
        """
        Run all steps. 
        """
        for step in self.generate_steps(context=context):
            step.run()
