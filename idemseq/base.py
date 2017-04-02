class Options(dict):
    _valid_options = {}

    def __init__(self, *args, **kwargs):
        super(Options, self).__init__(*args, **kwargs)
        for k in self:
            if k not in self._valid_options:
                raise ValueError('Unsupported {}.{}'.format(self.__class__.__name__, k))

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

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True
