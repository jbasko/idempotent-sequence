import argparse
import logging

from idemseq.log import configure_logging
from idemseq.sequence import SequenceBase


example = SequenceBase()


@example.command(run_always=True)
def greeting(name):
    print('Hello {}'.format(name))


@example.command
def check_time_is_good():
    assert True


def main():
    configure_logging(log_level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', help='Path to SQLite database to use', default='/tmp/example-01.db')
    parser.add_argument('--reset', action='store_true', help='Forget previous progress and exit')
    parser.add_argument('--dry-run', action='store_true', help='Just simulate a run')
    parser.add_argument('--name', help='A dummy argument to pass to the command sequence')

    args = parser.parse_args()

    sequence = example(args.run_id, dry_run=args.dry_run)
    if args.reset:
        sequence.reset()
        return

    sequence.run(context=dict(name=args.name))


if __name__ == '__main__':
    main()
