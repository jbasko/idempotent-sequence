import pytest

from idemseq.command import Command
from idemseq.sequence import SequenceCommand, SequenceBase


def test_command_registration():
    output = []
    appender = SequenceBase()

    @appender.command
    def first():
        output.append(1)

    @appender.command(name='second')
    def second_step():
        output.append(2)

    @appender.command(run_always=True)
    def third_step():
        output.append(3)

    @appender.command
    def fourth_step(a, b, c=3):
        output.append(a + b + c)

    assert output == []

    seq = appender()

    seq.run(context=dict(a=1, b=2))
    assert output == [1, 2, 3, 6]

    # Will run the third_step again
    seq.run(context=dict(a=1, b=2))
    assert output == [1, 2, 3, 6, 3]

    # Reset and will run all steps again
    seq.reset()
    seq.run(context=dict(a=5, b=6, c=7))
    assert output == [1, 2, 3, 6, 3, 1, 2, 3, 18]


def test_steps_are_run_once():
    outputs = []

    def append_to_output():
        outputs.append(1)

    seq = SequenceBase(
        Command(append_to_output, name='one'),
        Command(append_to_output, name='two'),
    )

    invocation1 = seq()

    invocation1.run()
    assert len(outputs) == 2

    invocation1.run()
    assert len(outputs) == 2

    invocation1.run()
    assert len(outputs) == 2

    # A different example

    invocation2 = seq()
    invocation2.run()

    assert len(outputs) == 4


def test_run_always_and_run_until_finished_are_respected():
    outputs = []

    seq = SequenceBase()

    @seq.command
    def append_1_to_output():
        outputs.append(1)

    @seq.command(run_always=True)
    def append_2_to_output():
        outputs.append(2)

    @seq.command(run_until_finished=True)
    def append_3_to_output():
        outputs.append(3)

    @seq.command
    def append_done_to_output():
        if len(outputs) > 5:
            outputs.append('done')
        else:
            raise Exception('outputs is short -- {}'.format(len(outputs)))

    appender = seq()
    assert outputs == []

    appender.run(warn_only=True)
    assert outputs == [1, 2, 3]

    appender.run(warn_only=True)
    assert outputs == [1, 2, 3, 2, 3]

    appender.run(warn_only=True)
    assert outputs == [1, 2, 3, 2, 3, 2, 3, 'done']

    # After it is finished, run_always still runs, run_until_finished does not
    appender.run(warn_only=True)
    assert outputs == [1, 2, 3, 2, 3, 2, 3, 'done', 2]


def test_context_is_injected_and_is_per_run():
    outputs = []

    def do_multiplication(x=1, y=10):
        outputs.append(x * y)

    multiplying_appender = SequenceBase(
        Command(do_multiplication, name='first', run_always=True),
        Command(do_multiplication, name='second', run_always=True),
    )

    sequence1 = multiplying_appender()

    sequence1.run(context=dict(x=2))
    assert outputs == [20, 20]

    # Make sure that x value from previous run isn't used
    sequence1.run(context=dict(y=5))
    assert outputs == [20, 20, 5, 5]


def test_order_is_respected():
    outputs = []

    appender = SequenceBase()

    @appender.command(order=300)
    def append_1_to_output():
        outputs.append(1)

    @appender.command(order=100)
    def append_2_to_output():
        outputs.append(2)

    @appender.command(order=200)
    def append_3_to_output():
        outputs.append(3)

    appender().run()
    assert outputs == [2, 3, 1]


def test_can_inspect_invocation_completion():
    assert SequenceBase()().is_finished

    seq = SequenceBase(Command(lambda: 1, name='first'))()
    assert not seq.is_finished

    seq.run()
    assert seq.is_finished


def test_can_inspect_and_run_step_individually():
    seq = SequenceBase(
        Command(lambda: 1, name='first'),
        Command(lambda: 2, name='second'),
        Command(lambda: 3, name='third'),
        Command(lambda: 4, name='fourth', run_always=True),
    )
    inv = seq()

    steps = list(inv)
    assert not steps[0].is_finished
    assert not steps[1].is_finished
    assert not steps[2].is_finished

    steps[0].run()
    assert steps[0].is_finished
    assert not steps[1].is_finished
    assert not steps[2].is_finished

    with pytest.raises(SequenceCommand.AlreadyCompleted):
        steps[0].run()

    with pytest.raises(SequenceCommand.PreviousStepsNotFinished):
        steps[2].run()

    steps[1].run()
    assert steps[0].is_finished
    assert steps[1].is_finished
    assert not steps[2].is_finished

    with pytest.raises(SequenceCommand.AlreadyCompleted):
        steps[0].run()

    with pytest.raises(SequenceCommand.AlreadyCompleted):
        steps[1].run()

    steps[2].run()
    assert steps[0].is_finished
    assert steps[1].is_finished
    assert steps[2].is_finished

    with pytest.raises(SequenceCommand.AlreadyCompleted):
        steps[2].run()

    assert not steps[3].is_finished
    assert not inv.is_finished

    steps[3].run()
    assert steps[3].is_finished
    assert inv.is_finished

    # Still runnable because run_always=True
    steps[3].run()
