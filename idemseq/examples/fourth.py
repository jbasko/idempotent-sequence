from idemseq.examples.util import configure_logging
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
    configure_logging()
    sequence = example('/tmp/fourth-example.db', context=dict(name='Untitled'))
    sequence.reset()

    assert sequence.context.name == 'Untitled'

    with sequence.env(warn_only=True):
        assert sequence.run_options.warn_only is True

        assert sequence.context.name == 'Untitled'

        with sequence.env(context=dict(name='Bob')):
            assert sequence.run_options.warn_only is True
            assert 'name' in sequence.context
            assert sequence.context.name == 'Bob'
            sequence.run()

        assert sequence.context.name == 'Untitled'

        with sequence.env(context=dict(name='Bobby')):
            assert 'name' in sequence.context
            assert sequence.context.name == 'Bobby'
            sequence['print_greeting'].run()

        assert sequence.context.name == 'Untitled'

