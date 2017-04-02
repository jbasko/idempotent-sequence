import pytest

from idemseq.base import Options, AttrDict


def test_nested_attr_dict():
    first = AttrDict(a=1, b=2, c=3)

    second = AttrDict(d=4)
    second.set_parent(first)

    third = AttrDict(b=222)
    third.set_parent(second)

    assert first.a == 1
    assert first.b == 2
    assert first.c == 3
    with pytest.raises(AttributeError):
        assert first.d != 4

    assert second.a == 1
    assert second.b == 2
    assert second.c == 3
    assert second.d == 4

    assert third.a == 1
    assert third.b == 222
    assert third.c == 3
    assert third.d == 4

    assert 'a' in third
    assert 'b' in third
    assert 'c' in third
    assert 'd' in third
    assert 'd' not in first
    assert 'e' not in third


def test_nested_options():
    class CustomOptions(Options):
        _valid_options = {
            'a': 1,
            'b': 2,
            'c': 3,
        }

    first = CustomOptions(a=11)

    second = CustomOptions(b=22)
    second.set_parent(first)

    third = CustomOptions(c=33)
    third.set_parent(second)

    fourth = CustomOptions(b=44)
    fourth.set_parent(third)

    assert (first.a, first.b, first.c) == (11, 2, 3)
    assert (second.a, second.b, second.c) == (11, 22, 3)
    assert (third.a, third.b, third.c) == (11, 22, 33)
    assert (fourth.a, fourth.b, fourth.c) == (11, 44, 33)

    assert 'a' in fourth
    assert 'b' in fourth
    assert 'c' in fourth
    assert 'd' not in fourth
