import pytest

from idemseq.idempotent_sequence import Step, Command
from idemseq.persistence import SqliteStepRegistry


def test_sqlite_step_registry():
    step = Step(index=1, command=Command(lambda: 1, name='first'))

    reg = SqliteStepRegistry(':memory:')

    assert not reg.get_known_statuses()
    assert reg.get_status(step) == Step.status_unknown

    reg.update_status(step, Step.status_finished)
    assert reg.get_status(step) == Step.status_finished
    assert reg.get_known_statuses() == {'first': 'finished'}

    reg.update_status(step, Step.status_unknown)
    assert reg.get_known_statuses() == {'first': Step.status_unknown}
    assert reg.get_status(step) == Step.status_unknown

    with pytest.raises(ValueError):
        reg.update_status(step, 'some_invalid_status')
