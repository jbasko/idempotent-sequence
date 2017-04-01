import pytest

from idemseq.command import Command
from idemseq.sequence import SequenceCommand
from idemseq.persistence import SqliteStateRegistry


def test_sqlite_step_registry():
    step = SequenceCommand(command=Command(lambda: 1, name='first'))

    reg = SqliteStateRegistry(':memory:')

    assert not reg.get_known_statuses()
    assert reg.get_status(step) == SequenceCommand.status_unknown

    reg.update_status(step, SequenceCommand.status_finished)
    assert reg.get_status(step) == SequenceCommand.status_finished
    assert reg.get_known_statuses() == {'first': 'finished'}

    reg.update_status(step, SequenceCommand.status_unknown)
    assert reg.get_known_statuses() == {'first': SequenceCommand.status_unknown}
    assert reg.get_status(step) == SequenceCommand.status_unknown

    with pytest.raises(ValueError):
        reg.update_status(step, 'some_invalid_status')
