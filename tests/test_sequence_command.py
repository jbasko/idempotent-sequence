import pytest

from idemseq.command import Command
from idemseq.sequence import SequenceBase


@pytest.fixture
def one_command_sequence_base():
    return SequenceBase(
        Command(lambda: 0, name='command_0'),
    )


def test_sequence_command_interface(one_command_sequence_base):
    sequence = one_command_sequence_base()

    sequence_command = sequence['command_0']

    assert not sequence_command.is_finished

    # Should do nothing as there is no state
    sequence_command.reset()
    assert not sequence_command.is_finished

    # Should set status to finished
    sequence_command.run()
    assert sequence_command.is_finished

    # Should reset status to unknown
    sequence_command.reset()
    assert not sequence_command.is_finished

    # Running the entire sequence should set individual command's status to finished
    sequence.run()
    assert sequence.is_finished
    assert sequence_command.is_finished

    # Resetting the command state should reset the sequence state
    sequence_command.reset()
    assert not sequence.is_finished
    assert not sequence_command.is_finished
