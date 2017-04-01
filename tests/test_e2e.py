from idemseq.idempotent_sequence import CommandSequence, Command


def test_command_registration():
    seq = CommandSequence()

    @seq.command
    def first():
        return 1

    @seq.command(name='second')
    def second_step():
        return 2

    @seq.command(run_always=True)
    def third_step():
        return 3

    @seq.command
    def fourth_step(a, b, c=3):
        return a + b + c

    # Commands should be registered with the right name
    assert len(seq.commands) == 4
    assert 'first' in seq.commands
    assert 'second' in seq.commands
    assert 'second_step' not in seq.commands
    assert 'third' not in seq.commands
    assert 'third_step' in seq.commands
    assert 'fourth_step' in seq.commands

    assert isinstance(seq.commands['first'], Command)
    assert isinstance(seq.commands['second'], Command)

    # Command options
    assert seq.commands['first'].options.run_always is None
    assert seq.commands['second'].options.run_always is None
    assert seq.commands['third_step'].options.run_always is True
    assert seq.commands['fourth_step'].options.run_always is None

    seq.run_without_registration(context=dict(a=1, b=2))


def test_steps_are_run_once():
    outputs = []

    def append_to_output():
        outputs.append(1)

    seq = CommandSequence(
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

    # A different invocation

    invocation2 = seq()
    invocation2.run()

    assert len(outputs) == 4


def test_run_always_is_respected():
    outputs = []

    seq = CommandSequence()

    @seq.command
    def append_1_to_output():
        outputs.append(1)

    @seq.command(run_always=True)
    def append_2_to_output():
        outputs.append(2)

    @seq.command
    def append_3_to_output():
        outputs.append(3)

    invocation = seq()

    invocation.run()
    assert outputs == [1, 2, 3]

    invocation.run()
    assert outputs == [1, 2, 3, 2]

    invocation.run()
    assert outputs == [1, 2, 3, 2, 2]


def test_context_is_injected_and_replaced_entirely_if_specified_on_run():
    outputs = []

    def do_multiplication(x, y=10):
        outputs.append(x * y)

    seq = CommandSequence(
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

    seq = CommandSequence()

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
