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