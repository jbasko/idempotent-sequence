class Step(object):
    """
    Represents a Command in the context of an CommandSequenceInvocation.
    
    Step can be considered a concrete Command.
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

    def __init__(self, index, command, invocation=None):
        super(Step, self).__init__()
        self._index = index
        self._command = command
        self._invocation = invocation

    def __getattr__(self, item):
        return getattr(self._command, item)

    def __setattr__(self, key, value):
        if key in ('_index', '_command', '_invocation'):
            return super(Step, self).__setattr__(key, value)
        else:
            return setattr(self._command, key, value)

    @property
    def index(self):
        return self._index

    def run(self):
        if self._invocation.step_registry.get_status(self) == self.status_finished:
            if not self.options.run_always:
                raise self.AlreadyCompleted(self.name)

        kwargs = {}
        for param in self._command.parameters:
            if param.name in self._invocation.context:
                kwargs[param.name] = self._invocation.context[param.name]

        result = self._command(**kwargs)
        self._invocation.step_registry.update_status(self, self.status_finished)

        return result


class CommandSequenceInvocation(object):
    """
    CommandSequenceInvocation is a concrete instance of CommandSequence.
    
    An invocation may be run multiple times.
    """
    step_registry_cls = None

    def __init__(self, sequence, context=None, step_registry_name=None):
        self._sequence = sequence
        self._context = context or {}

        step_registry_cls = self.step_registry_cls
        if step_registry_cls is None:
            from idemseq.persistence import SqliteStepRegistry
            step_registry_cls = SqliteStepRegistry
        self._step_registry = step_registry_cls(name=step_registry_name)

    @property
    def context(self):
        return self._context

    @property
    def step_registry(self):
        return self._step_registry

    def __iter__(self):
        for index, command in enumerate(self._sequence):
            yield Step(index=index, command=command, invocation=self)

    def run(self, context=None):
        """
        Runs the sequence of steps.
        
        :param context: dict -- if context is not None, it will replace the invocation's original context entirely. 
        """
        if context is not None:
            self._context = context
        for step in self:
            try:
                step.run()
            except Step.AlreadyCompleted:
                continue
