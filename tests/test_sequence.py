import pytest

from idemseq.sequence import SequenceBase, Sequence, SequenceCommand


@pytest.fixture
def hello_square_sequence_base(hello_world_command, square_command):
    return SequenceBase(hello_world_command, square_command)


def test_calling_sequence_base_returns_sequence(hello_square_sequence_base):
    sequence = SequenceBase()()
    assert isinstance(sequence, Sequence)

    assert isinstance(hello_square_sequence_base, SequenceBase)
    sequence = hello_square_sequence_base()
    assert isinstance(sequence, Sequence)


def test_can_access_sequence_commands_by_name(hello_square_sequence_base):
    sequence = hello_square_sequence_base()

    assert isinstance(sequence, Sequence)

    assert 'hello_world' in sequence
    assert isinstance(sequence['hello_world'], SequenceCommand)
    assert sequence['hello_world'].command == hello_square_sequence_base['hello_world']

    assert 'square' in sequence
    assert isinstance(sequence['square'], SequenceCommand)
    assert sequence['square'].command == hello_square_sequence_base['square']

    assert 'something_else' not in sequence
    with pytest.raises(KeyError):
        assert sequence['something_else']


def test_reset_sets_all_command_statuses_to_unknown(hello_world_command, square_command):
    seq = SequenceBase(hello_world_command, square_command)()

    assert not seq.is_finished
    assert not seq['hello_world'].is_finished
    assert not seq['square'].is_finished

    seq.run(dict(x=5))

    assert seq.is_finished
    assert seq['hello_world'].is_finished
    assert seq['square'].is_finished

    seq.reset()

    assert not seq.is_finished
    assert not seq['hello_world'].is_finished
    assert not seq['square'].is_finished

    seq.run(dict(x=5))

    assert seq.is_finished
    assert seq['hello_world'].is_finished
    assert seq['square'].is_finished

    seq['hello_world'].reset()

    assert not seq.is_finished
    assert not seq['hello_world'].is_finished
    assert seq['square'].is_finished
