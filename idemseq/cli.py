import importlib

import click

from idemseq.controller import create_controller_cli


class IdemseqCli(click.MultiCommand):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('subcommand_metavar', 'BASE_MODULE:BASE_NAME ACTION ...')
        super(IdemseqCli, self).__init__(*args, **kwargs)

    def list_commands(self, ctx):
        return ()

    def get_command(self, ctx, cmd_name):
        base_module, base_name = cmd_name.split(':', 1)
        return create_controller_cli(getattr(importlib.import_module(base_module), base_name))


@click.command(cls=IdemseqCli)
def cli():
    pass


if __name__ == '__main__':
    cli()
