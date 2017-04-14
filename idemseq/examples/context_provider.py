import click

from idemseq.controller import create_controller_cli
from idemseq.sequence import SequenceBase


class Installer(SequenceBase):
    # @property
    # def name(self):
    #     return click.option('--name')
    pass


installer = Installer()


@installer.provider
def name():
    return 'Bob'


# @installer.cli_customisation
# def name():
#     return click.option('--name')


@installer.command
def say_hello(name):
    print('Hello, {}!'.format(name))


@installer.command
def say_bye(name):
    print('Bye, {}'.format(name))


if __name__ == '__main__':
    create_controller_cli(installer)()
