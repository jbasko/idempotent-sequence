"""
A dummy minimal example
"""
import logging

from idemseq.examples.util import configure_logging
from idemseq.sequence import SequenceBase

example = SequenceBase()


@example.command(run_always=True)
def make_sure_server_is_running():
    pass


@example.command
def install_packages():
    pass


@example.command
def do_something():
    pass


if __name__ == '__main__':
    configure_logging(log_level=logging.DEBUG)

    sequence = example('/tmp/third.db')

    # Call this to forget the completion state
    # sequence.reset()

    sequence.run()
