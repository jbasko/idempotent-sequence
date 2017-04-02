import pytest

from idemseq.command import Command
from idemseq.sequence import SequenceBase


@pytest.fixture
def one_command_sequence_base():
    return SequenceBase(
        Command(lambda: 0, name='scs_command_0'),
    )


def test_command_state_interface(one_command_sequence_base):
    sequence_state = one_command_sequence_base()

    command_state = list(sequence_state)[0]

    assert not command_state.is_finished

    # Should do nothing as there is no state
    command_state.reset()
    assert not command_state.is_finished

    # Should set status to finished
    command_state.run()
    assert command_state.is_finished

    # Should reset status to unknown
    command_state.reset()
    assert not command_state.is_finished

    # Running the entire sequence should set individual command's status to finished
    sequence_state.run()
    assert sequence_state.is_finished
    assert command_state.is_finished

    # Resetting the command state should reset the sequence state
    command_state.reset()
    assert not sequence_state.is_finished
    assert not command_state.is_finished
