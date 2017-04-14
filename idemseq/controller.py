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
        # TODO Perhaps use context to get the right sequence when we allow more than
        # TODO one instance of the same base
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
    @click.pass_context
    def cli(ctx, **context):
        context_ = ctx.ensure_object(dict)
        context_.update(context)

    @cli.command(name='list')
    @click.pass_obj
    def list_(context):
        sequence = get_sequence()
        with sequence.env(context=context):
            for command in sequence.all_commands:
                click.echo(' * {} ({})'.format(command.name, command.status))

    # Note the missing cli.command() -- that's because run is registered below.
    @click.argument('selector', type=command_choice, required=False)
    @click.option('--dry-run', is_flag=True)
    @click.option('--force', is_flag=True)
    @click.option('--start-at', type=command_choice)
    @click.option('--stop-before', type=command_choice)
    @click.pass_obj
    def run(context, selector, **run_options):
        sequence = get_sequence()
        with sequence.env(context=context):
            if not selector:
                sequence.run(**run_options)
            else:
                with sequence.env(**run_options):
                    sequence[selector].run()

    for actualrun_option in base._actualrun_options:
        run = actualrun_option(run)
    cli.command()(run)

    @cli.command()
    @click.argument('selector', type=all_or_command_choice)
    @click.pass_obj
    def reset(context, selector):
        sequence = get_sequence()
        with sequence.env(context=context):
            if selector == 'all':
                sequence.reset()
            else:
                sequence[selector].reset()

    @cli.command()
    @click.argument('selector', type=command_choice)
    @click.argument('status', type=status_choice)
    @click.pass_obj
    def mark(context, selector, status):
        sequence = get_sequence()
        with sequence.env(context=context):
            sequence[selector].status = status

    for cli_wrapper in base._cli_wrappers:
        cli = cli_wrapper()(cli)

    return cli
