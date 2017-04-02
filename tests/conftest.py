import logging

import pytest

from idemseq.command import Command
from idemseq.log import configure_logging
from idemseq.sequence import SequenceBase

configure_logging(log_level=logging.DEBUG)


@pytest.fixture
def hello_world_command():
    def hello_world():
        print('Hello, world!')
    return Command(hello_world)


@pytest.fixture
def square_command():
    return Command(lambda x: x * x, name='square')


@pytest.fixture
def three_appenders_sequence_base():

    base = SequenceBase()
    base.outputs = []

    @base.command
    def appender1():
        base.outputs.append(1)

    @base.command
    def appender2():
        base.outputs.append(2)

    @base.command
    def appender3():
        base.outputs.append(3)

    return base
