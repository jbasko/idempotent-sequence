import importlib
import inspect
import logging

import click

from idemseq.command import Command
from idemseq.controller import create_controller_cli
from idemseq.inspector import Inspector
from idemseq.sequence import SequenceBase


log = logging.getLogger(__name__)


class IdemseqCli(click.MultiCommand):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('subcommand_metavar', 'BASE_MODULE:BASE_NAME ACTION ...')
        super(IdemseqCli, self).__init__(*args, **kwargs)

    def list_commands(self, ctx):
        return ()

    def get_command(self, ctx, cmd_name):
        if ':' in cmd_name:
            base_module_name, base_name = cmd_name.split(':', 1)
            base = getattr(importlib.import_module(base_module_name), base_name)
            if not isinstance(base, SequenceBase):
                raise ValueError('Expected base to be an instance of {}, got a {}'.format(
                    SequenceBase.__name__,
                    type(base).__name__,
                ))
        else:
            base_module_name = cmd_name
            base_module = importlib.import_module(base_module_name)
            bases = list(inspect.getmembers(base_module, lambda x: isinstance(x, SequenceBase)))
            if bases:
                if len(bases) != 1:
                    raise ValueError('More than one base found in module {}: {}'.format(
                        base_module_name,
                        bases,
                    ))
                base = bases[0][1]
            else:
                # Expose all functions in the module
                log.warning('No sequence bases found in module {}, exposing all non-private functions'.format(
                    base_module_name
                ))
                commands = []
                for func_name in Inspector(base_module).get_function_names():
                    if func_name.startswith('_'):
                        continue
                    commands.append(Command(getattr(base_module, func_name)))

                base = SequenceBase(*commands, auto_generate_command_run_options=True)

        return create_controller_cli(base)


@click.command(cls=IdemseqCli)
def cli():
    pass


if __name__ == '__main__':
    cli()
