from idemseq.sequence import SequenceBase

example = SequenceBase()


@example.command
def print_greeting(name):
    print('Hello, {}!'.format(name))


@example.command
def do_something():
    pass


@example.command(run_always=True)
def print_summary():
    pass


if __name__ == '__main__':
    # Can pass run options when initialising Sequence
    sequence = example('/tmp/fourth-example.db')

    print(sequence)

    # with sequence(dry_run=True):
    #     # Can pass user context when running the Sequence or its commands
    #     with sequence.user_data(name='Bob'):
    #         sequence.run()
    #
    #     sequence['print_greeting'].run(name='Bobby')
