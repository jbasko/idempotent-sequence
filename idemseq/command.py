import logging

from funcsigs import signature

from idemseq.base import Options

log = logging.getLogger(__name__)


class CommandOptions(Options):
    _valid_options = {
        'name': None,
        'order': -1,
        'run_always': None,
        'run_until_finished': None,
    }


class Command(object):
    """
    Represents a function and its meta information (run_options) to be used
    when the function is run as part of a sequence.
    """

    def __init__(self, func=None, **options):
        self._func = func

        self._options = CommandOptions(options)

        self._signature = None
        if self._func:
            self._signature = signature(self._func)

    def __str__(self):
        return '{}(name={})'.format(self.__class__.__name__, self.name)

    def __repr__(self):
        return '<{}>'.format(self)

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
    def description(self):
        if self._func:
            return self._func.__doc__
        return None

    def __call__(self, *args, **kwargs):
        log.debug('Command "{}" starting'.format(self.name))
        try:
            result = self._func(*args, **kwargs)
            log.debug('Command "{}" finished'.format(self.name))
            return result
        except Exception:
            log.error('Command "{}" failed with an exception'.format(self.name))
            raise

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._func == other._func and self._options == other._options
