import inspect
import logging


log = logging.getLogger(__name__)


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

    def __setattr__(self, key, value):
        if key in self._valid_options:
            self[key] = value
        else:
            raise AttributeError(key)


class Command(object):
    """
    Represents a function and its meta information (options) to be used
    when the function is run as part of a sequence.
    """

    def __init__(self, func=None, **options):
        self._func = func

        self._options = CommandOptions(options)

        self._signature = None
        if self._func:
            self._signature = inspect.signature(self._func)

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
