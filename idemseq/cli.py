import importlib

import click


def sequence_base_option(f):
    def callback(ctx, param, value):
        if value:
            module_name, base_name = value.split(':')
            m = importlib.import_module(module_name)
            return getattr(m, base_name)
        else:
            return None

    return click.argument(
        'sequence_base',
        expose_value=True,
        default=None,
        callback=callback,
        required=True,
    )(f)


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@sequence_base_option
def run(sequence_base):
    sequence = sequence_base()
    sequence.run()


@cli.command()
@sequence_base_option
def reset(sequence_base):
    sequence = sequence_base()
    sequence.reset()


@cli.command()
@sequence_base_option
def status(sequence_base):
    sequence = sequence_base()
    for command in sequence.all_commands:
        click.echo(' * {} - {}'.format(command.name, command.status))


if __name__ == '__main__':
    cli()
