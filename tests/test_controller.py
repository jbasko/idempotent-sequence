import uuid

import pytest
from click.testing import CliRunner

from idemseq.controller import create_controller_cli
from idemseq.sequence import SequenceBase


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def unique_cli_env(monkeypatch, tmpdir):
    f = tmpdir.join(str(uuid.uuid4()))
    monkeypatch.setenv('IDEMSEQ_SEQUENCE_ID', f)


@pytest.fixture
def dummy_cli():
    dummy = SequenceBase()

    @dummy.command
    def hello():
        """
        Prints hello.
        """
        print('Hello!')

    @dummy.command
    def bye():
        """
        Prints bye.
        """
        print('Bye!')

    return create_controller_cli(dummy)


def test_creates_controller_cli(unique_cli_env, cli_runner, dummy_cli):
    assert dummy_cli


def test_dummy_cli_displays_help(unique_cli_env, cli_runner, dummy_cli):
    help_result = cli_runner.invoke(dummy_cli, ['--help'])
    assert help_result.exit_code == 0

    help_result2 = cli_runner.invoke(dummy_cli)
    assert help_result2.exit_code == 0


def test_dummy_cli_lists_steps(unique_cli_env, cli_runner, dummy_cli):
    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (unknown)' in list_result.output
    assert '* bye (unknown)' in list_result.output

    assert cli_runner.invoke(dummy_cli, ['run']).exit_code == 0

    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (finished)' in list_result.output
    assert '* bye (finished)' in list_result.output


def test_dummy_cli_runs_all_steps(unique_cli_env, cli_runner, dummy_cli):
    run_result = cli_runner.invoke(dummy_cli, ['run'])
    assert run_result.exit_code == 0

    assert 'Hello!' in run_result.output
    assert 'Bye!' in run_result.output

    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (finished)' in list_result.output
    assert '* bye (finished)' in list_result.output

    # Repeated run still is ok
    assert cli_runner.invoke(dummy_cli, ['run']).exit_code == 0


def test_dummy_cli_runs_single_step(unique_cli_env, cli_runner, dummy_cli):
    run_result = cli_runner.invoke(dummy_cli, ['run', 'hello'])
    assert run_result.exit_code == 0

    assert 'Hello!' in run_result.output
    assert 'Bye!' not in run_result.output

    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (finished)' in list_result.output
    assert '* bye (unknown)' in list_result.output

    # Can run single step again, it just won't do anything
    run_result = cli_runner.invoke(dummy_cli, ['run', 'hello'])
    assert run_result.exit_code == 0


def test_dummy_cli_run_respects_dry_run(unique_cli_env, cli_runner, dummy_cli):
    run_result = cli_runner.invoke(dummy_cli, ['run', 'hello', '--dry-run'])
    assert run_result.exit_code == 0
    assert 'Hello!' not in run_result.output

    run_result = cli_runner.invoke(dummy_cli, ['run', '--dry-run'])
    assert run_result.exit_code == 0
    assert 'Hello!' not in run_result.output
    assert 'Bye!' not in run_result.output


def test_dummy_cli_run_respects_start_at_and_stop_before(unique_cli_env, cli_runner, dummy_cli):
    # Run hello so we can start at bye
    assert cli_runner.invoke(dummy_cli, ['run', 'hello']).exit_code == 0

    run_result = cli_runner.invoke(dummy_cli, ['run', '--start-at', 'bye'])
    assert run_result.exit_code == 0
    assert 'Hello!' not in run_result.output
    assert 'Bye!' in run_result.output

    # Reset everything so we can run from beginning
    assert cli_runner.invoke(dummy_cli, ['reset', 'all']).exit_code == 0

    run_result = cli_runner.invoke(dummy_cli, ['run', '--stop-before', 'bye'])
    assert run_result.exit_code == 0
    assert 'Hello!' in run_result.output
    assert 'Bye!' not in run_result.output

    # Run all, hello should not run again
    run_result = cli_runner.invoke(dummy_cli, ['run'])
    assert run_result.exit_code == 0
    assert 'Hello!' not in run_result.output
    assert 'Bye!' in run_result.output


def test_dummy_cli_resets_all_steps(unique_cli_env, cli_runner, dummy_cli):
    reset_result = cli_runner.invoke(dummy_cli, ['reset', 'all'])
    assert reset_result.exit_code == 0

    # Run sequence so we have something to reset
    assert cli_runner.invoke(dummy_cli, ['run']).exit_code == 0

    reset_result = cli_runner.invoke(dummy_cli, ['reset', 'all'])
    assert reset_result.exit_code == 0

    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (unknown)' in list_result.output
    assert '* bye (unknown)' in list_result.output


def test_dummy_cli_resets_single_step(unique_cli_env, cli_runner, dummy_cli):
    # Run sequence so we have something to reset
    assert cli_runner.invoke(dummy_cli, ['run']).exit_code == 0

    reset_result = cli_runner.invoke(dummy_cli, ['reset', 'bye'])
    assert reset_result.exit_code == 0

    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (finished)' in list_result.output
    assert '* bye (unknown)' in list_result.output

    # Resetting again should make no difference
    reset_result = cli_runner.invoke(dummy_cli, ['reset', 'bye'])
    assert reset_result.exit_code == 0

    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (finished)' in list_result.output
    assert '* bye (unknown)' in list_result.output


def test_dummy_cli_marks_step(unique_cli_env, cli_runner, dummy_cli):
    assert cli_runner.invoke(dummy_cli, ['mark', 'hello', 'finished']).exit_code == 0
    assert cli_runner.invoke(dummy_cli, ['mark', 'bye', 'failed']).exit_code == 0

    list_result = cli_runner.invoke(dummy_cli, ['list'])
    assert list_result.exit_code == 0
    assert '* hello (finished)' in list_result.output
    assert '* bye (failed)' in list_result.output
