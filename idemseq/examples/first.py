"""
An example that demonstrates all the features of the first version.
"""
import logging
import random
import time

from idemseq.examples.util import configure_logging
from idemseq.sequence import SequenceBase


log = logging.getLogger(__name__)

example = SequenceBase()


# Mark a command that needs to run even if it has succeeded before
@example.command(run_always=True)
def greeting():
    pass


# Change the order of commands, defaults to the order in which they are declared
@example.command(order=1000)
def the_last_command():
    pass


# Command arguments are injected via run_context, default values are respected
@example.command
def second(random_number_generator, x=0.5):
    if random_number_generator() < x:
        raise Exception('Bad luck')


# Commands can be given custom names
@example.command(name='third')
def third_command(random_number_generator):
    if random_number_generator() < 0.5:
        raise Exception('Bad luck')


if __name__ == '__main__':
    configure_logging(log_level=logging.DEBUG)

    # Create a Sequence.
    # Sequence is associated with an SQLite database where its state is persisted between attempts.
    sequence = example('/tmp/first-example.db')

    # Forget the state from previous attempts.
    # If you don't do this then attempting to run this example again
    # will do nothing.
    sequence.reset()

    attempt_no = 0

    while not sequence.is_finished:
        attempt_no += 1

        try:
            log.info('Attempt number {}'.format(attempt_no))

            # Run and don't forget to pass run_context (if any of the commands need it)
            sequence.run(context=dict(random_number_generator=random.random))

        except Exception:
            # We are lazy, let's ignore exceptions
            time.sleep(3)
            pass

    log.info('All completed in {} attempt(s)'.format(attempt_no))
