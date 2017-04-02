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


def test_str_representation(hello_square_sequence_base):
    sequence = hello_square_sequence_base()
    print(str(sequence))
    assert str(sequence) == '<Sequence (hello_world, square)>'


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


def test_dry_run(three_appenders_sequence_base, tmpdir):
    base = three_appenders_sequence_base
    sequence = base(tmpdir.join('test_dry_run.db').strpath)

    assert base.outputs == []

    with sequence.env(dry_run=True):
        sequence.run()

    assert base.outputs == []

    with sequence.env():
        sequence.run()

    assert base.outputs == [1, 2, 3]

    # This has no effect because sequence is finished, nothing to do
    with sequence.env(dry_run=True):
        sequence.run()
    assert base.outputs == [1, 2, 3]


def test_start_at_run_option(three_appenders_sequence_base):
    base = three_appenders_sequence_base
    sequence = three_appenders_sequence_base()
    assert base.outputs == []

    sequence.run(start_at='appender2')
    assert not sequence.is_finished
    assert base.outputs == [2, 3]

    with pytest.raises(ValueError):
        sequence.run(start_at='nonexistent')

    assert base.outputs == [2, 3]

    sequence.run(start_at='appender1')
    assert base.outputs == [2, 3, 1]


def test_stop_before_run_option(three_appenders_sequence_base):
    base = three_appenders_sequence_base
    sequence = three_appenders_sequence_base()
    assert base.outputs == []

    sequence.run(stop_before='appender2')
    assert base.outputs == [1]

    sequence.run(stop_before='appender3')
    assert base.outputs == [1, 2]

    with pytest.raises(ValueError):
        sequence.run(stop_before='nonexistent')

    assert not sequence.is_finished
