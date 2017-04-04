import copy

import pytest

from idemseq.sequence import SequenceBase, Sequence, SequenceCommand


def test_initialises_empty_sequence_base():
    sb = SequenceBase()
    assert len(sb) == 0
    assert 'hello_world' not in sb


def test_initialises_sequence_base(hello_world_command, square_command):
    sb = SequenceBase(hello_world_command, square_command)
    assert 'hello_world' in sb
    assert 'square' in sb
    assert 'something_else' not in sb

    assert len(sb) == 2

    assert sb.index_of('square') == 1
    assert sb.index_of('hello_world') == 0

    commands = list(sb)
    assert len(commands) == 2
    assert commands[0] == hello_world_command
    assert commands[1] == square_command


def test_does_not_accept_commands_with_same_name(hello_world_command, square_command):
    with pytest.raises(ValueError):
        SequenceBase(hello_world_command, hello_world_command)

    with pytest.raises(ValueError):
        SequenceBase(square_command, hello_world_command, square_command)


def test_sequence_base_does_not_modify_command_options(hello_world_command, square_command):
    hello_world_options = copy.deepcopy(dict(hello_world_command.options))
    square_command_options = copy.deepcopy(dict(square_command.options))

    assert hello_world_command.options == hello_world_options
    assert square_command.options == square_command_options

    SequenceBase(square_command, hello_world_command)

    assert hello_world_command.options == hello_world_options
    assert square_command.options == square_command_options

    SequenceBase(hello_world_command, square_command)

    assert hello_world_command.options == hello_world_options
    assert square_command.options == square_command_options


def test_registers_commands_via_command_decorator():
    sb = SequenceBase()

    @sb.command
    def cmd2():
        return 2

    @sb.command
    def cmd1():
        return 1

    assert len(sb) == 2
    assert sb.index_of('cmd2') == 0
    assert sb.index_of('cmd1') == 1


def test_calling_instance_with_no_commands_creates_empty_sequence():
    sb = SequenceBase()
    seq = sb()
    assert isinstance(seq, Sequence)
    assert len(seq) == 0


def test_calling_instance_with_commands_creates_sequence(hello_world_command, square_command):
    seq1 = SequenceBase(hello_world_command, square_command)()
    assert len(seq1) == 2

    assert len(seq1) == 2
    assert isinstance(seq1['hello_world'], SequenceCommand)
    assert seq1['hello_world'].command == hello_world_command
    assert isinstance(seq1['square'], SequenceCommand)
    assert seq1['square'].command == square_command


def test_can_access_commands_by_name(hello_world_command, square_command):
    sb = SequenceBase(hello_world_command, square_command)
    assert sb['hello_world'] == hello_world_command
    assert sb['square'] == square_command
