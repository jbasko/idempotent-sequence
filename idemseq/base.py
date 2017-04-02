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


class DryRunResult(object):
    def __init__(self, **call_details):
        for k, v in call_details.items():
            setattr(self, k, v)