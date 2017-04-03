import argparse
import logging

from idemseq.log import configure_logging
from idemseq.sequence import SequenceBase


example = SequenceBase()


@example.command(run_always=True)
def greeting(name):
    """
    Prints a greeting using name supplied in context. 
    """
    print('Hello {}'.format(name))


@example.command
def step_one():
    """
    First things first. This docstring will appear as command description.
    """
    pass


@example.command
def step_two():
    pass


@example.command
def step_three():
    pass


@example.command
def step_four():
    pass


def main():
    configure_logging(log_level=logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('--run-id', help='Path to SQLite database to use, defaults to /tmp/example-01.db', default='/tmp/example-01.db')
    parser.add_argument('--name', help='A dummy argument to pass to the command sequence')

    parser.add_argument('--reset', action='store_true', help='Forget previous progress and exit')
    parser.add_argument('--list', action='store_true', help='List all commands and exit')
    parser.add_argument('--command', help='Attempt to run a single command, will fail if previous commands have not been completed')

    # Run options
    parser.add_argument('--dry-run', action='store_true', help='Just simulate a run')
    parser.add_argument('--start-at', help='Specify command to start with irrespective of completion of previous commands')
    parser.add_argument('--stop-before', help='Specify command before which to stop sequence execution')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--warn-only', action='store_true')

    args = parser.parse_args()

    context = dict(name=args.name)
    sequence = example(args.run_id, dry_run=args.dry_run, start_at=args.start_at, stop_before=args.stop_before, force=args.force, warn_only=args.warn_only)

    if args.reset:
        sequence.reset()
        return

    if args.list:
        for command in sequence:
            print(' * {} - {}'.format(command.name, 'completed' if command.is_finished else 'todo'))
            if command.description:
                print(command.description)
        return

    with sequence.env(context=context):

        if args.command:
            sequence[args.command].run()
            return
        else:
            sequence.run()


if __name__ == '__main__':
    main()
