import logging

from funcsigs import signature

from idemseq.base import Options, FunctionWrapper

log = logging.getLogger(__name__)


class CommandOptions(Options):
    _valid_options = {
        'name': None,
        'order': -1,
        'run_always': None,
        'run_until_finished': None,
    }


class Command(FunctionWrapper):
    options_class = CommandOptions

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self._signature = None
        if self._func:
            self._signature = signature(self._func)

    @property
    def parameters(self):
        """
        Returns a view of parameters from underlying function's signature.
        """
        return self._signature.parameters.values()

    def __call__(self, *args, **kwargs):
        log.debug('Command "{}" starting'.format(self.name))
        try:
            result = self._func(*args, **kwargs)
            log.debug('Command "{}" finished'.format(self.name))
            return result
        except Exception:
            log.error('Command "{}" failed with an exception'.format(self.name))
            raise
