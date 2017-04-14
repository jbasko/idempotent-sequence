import pytest

from idemseq.intuitive_module import Module


def test_e2e():
    m = Module('idemseq.examples.intuitive_interpretation')

    # Exposed functions can be referenced as attributes
    assert callable(m.say_hello)

    # Providers aren't exposed
    with pytest.raises(AttributeError):
        assert m.get_name

    # Neither are privates
    with pytest.raises(AttributeError):
        assert m._times

    assert 'name' in m._dependencies
    assert 'times' in m._dependencies
    assert 'more' in m._dependencies

    assert 'get_name' not in m._exposed_functions
    assert 'say_hello' in m._exposed_functions

    assert m._call_func(m.say_hello) is None
    assert m._call_func(m.multiply_name) == 'BobBobBobBobBob'
