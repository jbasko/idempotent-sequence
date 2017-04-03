from idemseq.sequence import SequenceBase


def test_dry_run(three_appenders_sequence_base):
    base = three_appenders_sequence_base
    sequence = base()

    assert sequence._dry_run_state_registry_instance is None

    assert base.outputs == []

    with sequence.env(dry_run=True):
        sequence.run()
        assert base.outputs == []
        assert sequence.is_finished

    assert not sequence.is_finished

    with sequence.env():
        sequence.run()
        assert sequence.is_finished

    assert sequence.is_finished
    assert base.outputs == [1, 2, 3]


def test_dry_run_state_registry_knows_everything():
    base = SequenceBase()

    @base.command
    def appender1():
        pass

    @base.command
    def appender2():
        pass

    @base.command
    def appender3():
        pass

    sequence = base()

    assert sequence._dry_run_state_registry_instance is None

    assert sequence['appender1'].is_finished is False
    assert sequence['appender2'].is_finished is False
    assert sequence['appender3'].is_finished is False

    with sequence.env(stop_before='appender2'):
        sequence.run()
        assert sequence.is_finished is False
        assert sequence['appender1'].is_finished is True
        assert sequence['appender2'].is_finished is False
        assert sequence['appender3'].is_finished is False

    assert sequence.is_finished is False
    assert sequence['appender1'].is_finished is True
    assert sequence['appender2'].is_finished is False
    assert sequence['appender3'].is_finished is False

    with sequence.env(dry_run=True):
        assert sequence.is_finished is False
        assert sequence['appender1'].is_finished is True
        assert sequence['appender2'].is_finished is False
        assert sequence['appender3'].is_finished is False

    sequence.run(stop_before='appender3')

    assert sequence.is_finished is False
    assert sequence['appender1'].is_finished is True
    assert sequence['appender2'].is_finished is True
    assert sequence['appender3'].is_finished is False

    with sequence.env(dry_run=True):
        assert sequence.is_finished is False
        assert sequence['appender1'].is_finished is True
        assert sequence['appender2'].is_finished is True
        assert sequence['appender3'].is_finished is False

        sequence.run()
        assert sequence.is_finished

    assert not sequence.is_finished

    with sequence.env(dry_run=True):
        assert sequence.is_finished

    assert not sequence.is_finished
