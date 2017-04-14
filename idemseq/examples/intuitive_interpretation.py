# A getter of something that matches a parameter name, must be a provider
def get_name():
    return 'Bob'


# Function name matches parameter name, must be a provider
def hello_format():
    return 'Hello, {name}'


# Function name still matches parameter name (underscore just means private, ok), must be a provider
def _times():
    return 5


def _get_bye_format():
    return 'Bye, {name} :)'


def say_hello(hello_format, name):
    print(hello_format.format(name=name))


def do_something(times):
    for i in range(times):
        print('Doing something')


def do_more(more=True):
    print('Doing more? - {}'.format(more))


def say_bye(bye_format, name):
    print(bye_format.format(name=name))
