import click

from idemseq.base import Empty
from idemseq.controller import create_controller_cli
from idemseq.sequence import SequenceBase


installer = SequenceBase()


@installer.provider
def greeting():
    return 'Hello, {name}!'


@installer.cli_wrapper
def name_option():

    def callback(ctx, param, value):
        context = ctx.ensure_object(dict)
        if value is not Empty:
            context[param.name] = value
        return value

    return click.option(
        '--name',
        callback=callback,
        expose_value=False,
        default=Empty,
    )


@installer.command
def greet_user(greeting, name):
    print(greeting.format(name=name))


@installer.command
def say_bye(name):
    print('Bye, {}'.format(name))


if __name__ == '__main__':
    create_controller_cli(installer)()
