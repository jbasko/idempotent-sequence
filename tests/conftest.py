import logging
import pytest

from idemseq.command import Command
from idemseq.examples.util import configure_logging


configure_logging(log_level=logging.DEBUG)


@pytest.fixture
def function_factory():
    def factory(return_value=None):
        def f():
            return return_value
    return factory


@pytest.fixture
def hello_world_command():
    def hello_world():
        print('Hello, world!')
    return Command(hello_world)


@pytest.fixture
def square_command():
    return Command(lambda x: x * x, name='square')
