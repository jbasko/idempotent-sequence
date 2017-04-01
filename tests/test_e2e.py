from idemseq.idempotent_sequence import IdempotentSequence, Command


def test_the_desired_interface():
    seq = IdempotentSequence()

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

    # Commands are the registered functions with their original function names
    assert isinstance(seq.commands['first'], Command)
    assert isinstance(seq.commands['second'], Command)

    # Run step by step
    for step in seq.generate_steps(context=dict(a=1, b=2)):
        step.run()

    # Run all in one go
    seq.run(context=dict(a=1, b=2))
