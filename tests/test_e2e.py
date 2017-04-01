import pytest

from idemseq.command import Command
from idemseq.sequence import SequenceCommand, SequenceBase


def test_command_registration():
    output = []
    seq = SequenceBase()

    @seq.command
    def first():
        output.append(1)

    @seq.command(name='second')
    def second_step():
        output.append(2)

    @seq.command(run_always=True)
    def third_step():
        output.append(3)

    @seq.command
    def fourth_step(a, b, c=3):
        output.append(a + b + c)

    assert output == []

    seq.run_without_registration(context=dict(a=1, b=2))
    assert output == [1, 2, 3, 6]

    # All steps will run again because we are not registering the state
    seq.run_without_registration(context=dict(a=1, b=2))
    assert output == [1, 2, 3, 6, 1, 2, 3, 6]


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


def test_run_always_is_respected():
    outputs = []

    seq = SequenceBase()

    @seq.command
    def append_1_to_output():
        outputs.append(1)

    @seq.command(run_always=True)
    def append_2_to_output():
        outputs.append(2)

    @seq.command
    def append_3_to_output():
        outputs.append(3)

    appender = seq()

    appender.run()
    assert outputs == [1, 2, 3]

    appender.run()
    assert outputs == [1, 2, 3, 2]

    appender.run()
    assert outputs == [1, 2, 3, 2, 2]


def test_context_is_injected_and_replaced_entirely_if_specified_on_run():
    outputs = []

    def do_multiplication(x, y=10):
        outputs.append(x * y)

    seq = SequenceBase(
        Command(do_multiplication, name='first'),
        Command(do_multiplication, name='second'),
    )

    invocation1 = seq(context=dict(x=2, y=3))
    invocation1.run()
    assert outputs == [6, 6]

    invocation2 = seq(context=dict(x=4, y=5))  # this context gets overwritten by context supplied to run
    invocation2.run(context=dict(x=10))
    assert outputs == [6, 6, 100, 100]


def test_order_is_respected():
    outputs = []

    seq = SequenceBase()

    @seq.command(order=300)
    def append_1_to_output():
        outputs.append(1)

    @seq.command(order=100)
    def append_2_to_output():
        outputs.append(2)

    @seq.command(order=200)
    def append_3_to_output():
        outputs.append(3)

    seq.run_without_registration()
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
