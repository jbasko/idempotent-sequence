import pytest

from idemseq.sequence import SequenceEnv, get_current_sequence_env, SequenceBase


def test_initialises_sequence_env(three_appenders_sequence_base):
    sequence = three_appenders_sequence_base()

    env = sequence.env()
    assert isinstance(env, SequenceEnv)


def test_accepts_context_and_other_run_options(three_appenders_sequence_base):
    sequence = three_appenders_sequence_base()

    env = sequence.env(dry_run=True, context=dict(x=10))
    assert env.run_options.dry_run is True
    assert env.context.x == 10


def test_is_a_context_manager(three_appenders_sequence_base):
    with three_appenders_sequence_base().env():
        pass


def test_manages_stack(three_appenders_sequence_base):
    sequence = three_appenders_sequence_base()

    # Must not raise RuntimeError because we push default env to sequence's env stack
    assert sequence.run_options
    assert sequence.context is not None

    with sequence.env(dry_run=True, context=dict(x=10)):
        with sequence.env(context=dict(y=20)):
            with sequence.env(warn_only=True):
                assert sequence.run_options.warn_only is True
                assert sequence.run_options.dry_run is True
                assert sequence.context.x == 10
                assert sequence.context.y == 20

                assert 'x' in sequence.context
                assert 'y' in sequence.context

            assert sequence.run_options.warn_only is False
            assert sequence.run_options.dry_run is True
            assert sequence.context.x == 10
            assert sequence.context.y == 20

        assert sequence.run_options.warn_only is False
        assert sequence.run_options.dry_run is True
        assert sequence.context.x == 10
        assert 'y' not in sequence.context

    assert sequence.run_options.warn_only is False
    assert sequence.run_options.dry_run is None
    assert 'x' not in sequence.context
    assert 'y' not in sequence.context

    # There must be just one env remaining in sequence env stack
    get_current_sequence_env(sequence.uid).pop()

    with pytest.raises(RuntimeError):
        get_current_sequence_env(sequence.uid).pop()


def test_context_is_injected_where_needed():
    dummy = SequenceBase()

    @dummy.command
    def needs_x(a, x):
        assert True

    @dummy.command
    def needs_y(a, y):
        assert True

    sequence = dummy(context=dict(a=1))

    with pytest.raises(TypeError):
        sequence.run()

    assert not sequence['needs_x'].is_finished
    assert not sequence['needs_y'].is_finished

    with pytest.raises(TypeError):
        sequence.run(context=dict(x=10))

    assert sequence['needs_x'].is_finished
    assert not sequence['needs_y'].is_finished

    # No need to supply x now because that command is not run anymore
    sequence.run(context=dict(y=20))

    assert sequence['needs_x'].is_finished
    assert sequence['needs_y'].is_finished
    assert sequence.is_finished
