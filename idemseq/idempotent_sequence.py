import inspect


class CommandOptions(dict):
    _valid_options = {
        'name': None,
        'order': None,
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

    @property
    def func(self):
        return self._func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Step(object):
    """
    Represents a Command in the context of an Invocation of a CommandSequence.
    """

    status_unknown = 'unknown'
    status_failed = 'failed'
    status_finished = 'finished'

    valid_statuses = (
        status_unknown,
        status_failed,
        status_finished,
    )

    def __init__(self, index, command, context=None):
        super(Step, self).__init__()
        self._index = index
        self._command = command
        self._context = context or {}

    def __getattr__(self, item):
        return getattr(self._command, item)

    def __setattr__(self, key, value):
        if key in ('_command', '_context', '_index'):
            return super(Step, self).__setattr__(key, value)
        else:
            return setattr(self._command, key, value)

    @property
    def index(self):
        return self._index

    def run(self):
        kwargs = {}
        for param in self._command.parameters:
            if param.name in self._context:
                kwargs[param.name] = self._context[param.name]
        return self._command(**kwargs)


class IdempotentSequence(object):
    def __init__(self):
        self._commands = {}

    @property
    def commands(self):
        return self._commands

    def command(self, f=None, **options):
        def decorator(func):
            options.setdefault('order', len(self._commands) + 1)  # The default order is the order of declaration
            command = Command(func=func, **options)
            self._commands[command.name] = command
            return command.func

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