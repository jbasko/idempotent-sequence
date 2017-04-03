import pytest

from idemseq.exceptions import SequenceCommandException
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


def test_start_at_run_option():
    """
    start_at specifies command with which to continue sequence execution.
    
    Unless forced, commands that are not ready, should not be run.
    
    Commands that are completed and don't have any options like run_always or run_until_finished,
    should not be run under any circumstances (user must reset state to execute an already completed command). 
    """
    base = SequenceBase()
    outputs = []

    @base.command
    def a():
        outputs.append('a')

    @base.command(run_always=True)
    def b():
        outputs.append('b')

    @base.command(run_until_finished=True)
    def c():
        outputs.append('c')

    sequence = base()

    with pytest.raises(SequenceCommandException):
        sequence.run(start_at='b')

    with pytest.raises(SequenceCommandException):
        sequence.run(start_at='c')

    sequence.run(start_at='a')
    assert outputs == ['a', 'b', 'c']

    sequence.run(start_at='a')
    assert outputs == ['a', 'b', 'c', 'b']

    sequence.run(start_at='b')
    assert outputs == ['a', 'b', 'c', 'b', 'b']

    sequence.run(start_at='c')
    assert outputs == ['a', 'b', 'c', 'b', 'b']

    sequence.run(start_at='a')
    assert outputs == ['a', 'b', 'c', 'b', 'b', 'b']

    with pytest.raises(ValueError):
        sequence.run(start_at='x')


def test_start_at_run_option_with_force(three_appenders_sequence_base):
    sequence = three_appenders_sequence_base()
    assert three_appenders_sequence_base.outputs == []

    with pytest.raises(SequenceCommandException):
        sequence.run(start_at='appender2')

    assert three_appenders_sequence_base.outputs == []

    sequence.run(start_at='appender2', force=True)

    assert three_appenders_sequence_base.outputs == [2, 3]


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


def test_running_command_before_its_dependencies_are_finished_raises_sequence_exception(three_appenders_sequence_base):
    sequence = three_appenders_sequence_base()

    with pytest.raises(SequenceCommandException):
        sequence['appender2'].run()

    with pytest.raises(SequenceCommandException):
        sequence.run(start_at='appender2')

    with pytest.raises(SequenceCommandException):
        sequence['appender3'].run()

    sequence['appender1'].run()

    with pytest.raises(SequenceCommandException):
        sequence['appender3'].run()

    sequence['appender2'].run()

    sequence['appender3'].run()


def test_force_option_allows_running_command_before_its_dependencies_are_finished(three_appenders_sequence_base):
    sequence = three_appenders_sequence_base()

    with pytest.raises(SequenceCommandException):
        sequence['appender2'].run()

    assert not sequence['appender2'].is_finished

    with sequence.env(force=True):
        sequence['appender2'].run()

    assert sequence['appender2'].is_finished
