def _something_private():
    # This shouldn't be exposed
    raise RuntimeError('This should not be exposed')


def something_public():
    print('Yeah, this is public')


def something_with_args(name):
    print('Hello, {}!'.format(name))
