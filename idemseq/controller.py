import click

from idemseq.log import configure_logging
from idemseq.sequence import SequenceCommand


def create_controller_cli(base):
    """
    From SequenceBase creates a runnable Command Line Interface (cli) based controller
    to manage sequences of this base.
    """

    scope = {}
    all_or_command_choice = click.Choice(('all',) + tuple(base._commands.keys()))
    command_choice = click.Choice(base._commands.keys())
    status_choice = click.Choice(SequenceCommand.valid_statuses)

    def get_sequence():
        if 'sequence' not in scope:
            scope['sequence'] = base(scope['sequence_id'])
        return scope['sequence']

    def sequence_id_callback(ctx, param, value):
        scope['sequence_id'] = value

    def log_level_callback(ctx, param, value):
        configure_logging(log_level=value)

    @click.group()
    @click.option(
        '--sequence-id',
        callback=sequence_id_callback,
        expose_value=False,
        required=True,
        envvar='IDEMSEQ_SEQUENCE_ID',
        default=':memory:',
    )
    @click.option(
        '--log-level',
        callback=log_level_callback,
        expose_value=False,
        type=click.Choice(['debug', 'info', 'warn', 'error']),
        envvar='IDEMSEQ_LOG_LEVEL',
        default='info',
    )
    def cli():
        pass

    @cli.command(name='list')
    def list_():
        for command in get_sequence().all_commands:
            click.echo(' * {} ({})'.format(command.name, command.status))

    @cli.command()
    @click.argument('selector', type=command_choice, required=False)
    @click.option('--dry-run', is_flag=True)
    @click.option('--force', is_flag=True)
    @click.option('--start-at', type=command_choice)
    @click.option('--stop-before', type=command_choice)
    def run(selector, **run_options):
        sequence = get_sequence()
        if not selector:
            sequence.run(**run_options)
        else:
            with sequence.env(**run_options):
                sequence[selector].run()

    @cli.command()
    @click.argument('selector', type=all_or_command_choice)
    def reset(selector):
        if selector == 'all':
            get_sequence().reset()
        else:
            get_sequence()[selector].reset()

    @cli.command()
    @click.argument('selector', type=command_choice)
    @click.argument('status', type=status_choice)
    def mark(selector, status):
        get_sequence()[selector].status = status

    return cli
