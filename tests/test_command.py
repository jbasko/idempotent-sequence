from idemseq.command import Command


def test_initialises_command_with_custom_options():
    c1 = Command(func=lambda: 1, name='first', run_always=True)
    assert c1.name == 'first'
    assert c1.options.run_always is True
    assert c1.options.order == -1
    assert c1() == 1
    assert not c1.parameters


def test_initialises_command_from_function():
    def first(a, b=10):
        return a + b

    c1 = Command(first)
    assert c1.name == 'first'
    assert not c1.options.run_always
    assert c1.options.order == -1
    assert c1(5) == 15
    assert [p.name for p in c1.parameters] == ['a', 'b']


def test_equality():
    def first(a):
        return a

    def second(a):
        return a

    c1 = Command(first)
    c11 = Command(first)
    c2 = Command(second)
    c22 = Command(second)

    assert c1 == c1
    assert c1 == c11
    assert c2 == c22
    assert c1 != c2


def test_str_representation():
    c1 = Command(func=lambda: 1, name='first')
    assert str(c1) == 'Command(name=first)'


def test_func_doc_is_command_description():
    def do_something():
        """
        This does something.
        """

    c1 = Command(func=do_something, name='c1')
    assert c1.description == '\n        This does something.\n        '

    c2 = Command(func=lambda: 1, name='c2')
    assert c2.description is None

    from idemseq.sequence import SequenceBase
    sequence = SequenceBase(c1, c2)()
    assert sequence['c1'].description == '\n        This does something.\n        '
    assert sequence['c2'].description is None


def test_func_doc_is_command_description_for_decorator_declared_commands():
    from idemseq.sequence import SequenceBase
    base = SequenceBase()

    @base.command
    def c3():
        """This does not do much"""

    assert base['c3'].description == 'This does not do much'

    sequence = base()

    assert sequence['c3'].description == 'This does not do much'
