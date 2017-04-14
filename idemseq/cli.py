import importlib
import inspect
import logging

import click
from slugify import slugify

from idemseq.command import Command
from idemseq.controller import create_controller_cli
from idemseq.intuitive_module import Module
from idemseq.sequence import SequenceBase


log = logging.getLogger(__name__)


class IdemseqCli(click.MultiCommand):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('subcommand_metavar', 'BASE_MODULE:BASE_NAME ACTION ...')
        super(IdemseqCli, self).__init__(*args, **kwargs)

    def list_commands(self, ctx):
        return ()

    def get_command(self, ctx, cmd_name):
        context = None

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
                log.warning('No sequence bases found in module {}, will use intuitive module interpretation!'.format(
                    base_module_name,
                ))

                # TODO context passing is a bit hacky, so we create context here?! that's dirty
                context = {}
                mod = Module(base_module, context=context)
                commands = [getattr(mod, func_name) for func_name in mod._exposed_functions]
                base = SequenceBase(*commands, auto_generate_command_run_options=False)
                for dep_name, dep_provider in mod._dependencies.items():
                    if dep_provider:
                        continue
                    base.actualrun_option(
                        '--{}'.format(slugify(dep_name)),
                        required=False,
                        # TODO should guess type from default value
                    )

        return create_controller_cli(base, base_context=context)


@click.command(cls=IdemseqCli)
def cli():
    pass


if __name__ == '__main__':
    cli()
