"""
Demonstrates how easy it is to create a command line interface to manage 
a sequence of commands.

Run this example with `python -m idemseq.examples.example02`

By default state is persisted in memory (so isn't persisted really).

To use a real store, specify path with --sequence=<path> or in environment
variable IDEMSEQ_SEQUENCE_ID.
"""

from idemseq.controller import create_controller_cli
from idemseq.sequence import SequenceBase


example = SequenceBase()


@example.command(run_always=True)
def greeting():
    print('Hello!')


@example.command
def step_one():
    pass


@example.command
def step_two():
    pass


@example.command
def step_three():
    pass


cli = create_controller_cli(example)


if __name__ == '__main__':
    cli()
