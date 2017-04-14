import funcsigs


class _Empty(object):
    def __bool__(self):
        return False

    def __nonzero__(self):
        # For Python2
        return False

    def __str__(self):
        return '<Empty>'

    def __repr__(self):
        return '<Empty>'


Empty = _Empty()


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self._parent_ = None

    def __getattr__(self, item):
        if super(AttrDict, self).__contains__(item):
            return self[item]
        elif self._parent_:
            return getattr(self._parent_, item)
        raise AttributeError(item)

    def __setattr__(self, key, value):
        if key == '_parent_':
            return super(AttrDict, self).__setattr__(key, value)
        if key in self:
            self[key] = value
            return
        raise AttributeError(key)

    def set_parent(self, parent):
        self._parent_ = parent

    def __contains__(self, item):
        if super(AttrDict, self).__contains__(item):
            return True
        elif self._parent_:
            return item in self._parent_
        else:
            return False


class Options(dict):
    _valid_options = {}

    def __init__(self, *args, **kwargs):
        super(Options, self).__init__(*args, **kwargs)
        self._parent_options_ = None
        for k in self:
            if k not in self._valid_options:
                raise ValueError('Unsupported {}.{}'.format(self.__class__.__name__, k))

    def __getattr__(self, item):
        if item in self._valid_options:
            if super(Options, self).__contains__(item):
                return self[item]
            elif self._parent_options_:
                return getattr(self._parent_options_, item)
            else:
                return self.get(item, self._valid_options[item])
        else:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        if key == '_parent_options_':
            return super(Options, self).__setattr__(key, value)
        if key in self._valid_options:
            self[key] = value
        else:
            raise AttributeError(key)

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    def set_parent(self, parent_options):
        self._parent_options_ = parent_options

    def __contains__(self, item):
        if super(Options, self).__contains__(item):
            return True
        elif self._parent_options_:
            return item in self._parent_options_
        else:
            return False


class OptionsWithName(Options):
    _valid_options = {
        'name': None
    }


class FunctionWrapper(object):
    options_class = OptionsWithName

    def __init__(self, func=None, **options):
        # self._func points to the original function and must not be modified.
        # decorators and other wrappers should work on self._executor instead.
        self._func = func

        self._options = self.options_class(options)
        self.__name__ = self.name

        self._signature = None
        if self._func:
            self._signature = funcsigs.signature(self._func)

        self._executor = self._default_executor

    @property
    def signature(self):
        return self._signature

    @property
    def parameters(self):
        """
        Returns a view of parameters from underlying function's signature.
        """
        return self.signature.parameters.values()

    @property
    def options(self):
        return self._options

    @property
    def name(self):
        return self.options.name or self._func.__name__

    @property
    def description(self):
        if self._func:
            return self._func.__doc__
        return None

    def _default_executor(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self._executor(*args, **kwargs)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._func == other._func and self._options == other._options

    def __str__(self):
        return '{}(name={})'.format(self.__class__.__name__, self.name)

    def __repr__(self):
        return '<{}>'.format(self)

    def get_dependencies(self):
        for p in self.parameters:
            yield p.name, Empty if p.default is funcsigs._empty else p.default


class DryRunResult(object):
    def __init__(self, **call_details):
        for k, v in call_details.items():
            setattr(self, k, v)