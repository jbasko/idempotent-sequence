import pytest

import idemseq.cli
from idemseq.intuitive_module import Module


def test_module():
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
    assert 'apples' in m._dependencies

    assert 'get_name' not in m._exposed_functions
    assert 'say_hello' in m._exposed_functions

    assert m.say_hello() is None
    assert m.multiply_name() == 'BobBobBobBobBob'


def test_options_injected_and_defaults_respected(cli_runner, unique_cli_env):
    help_result = cli_runner.invoke(idemseq.cli.cli, ['idemseq.examples.intuitive_interpretation', 'run', '--bye-format', 'See you later {name}!'])
    assert 'See you later Bob!' in help_result.output
    assert '5 apples and None pears' in help_result.output
    assert help_result.exit_code == 0


def test_unprovided_params_generate_required_options(cli_runner, unique_cli_env):
    help_result = cli_runner.invoke(idemseq.cli.cli, ['idemseq.examples.intuitive_interpretation', 'run'])
    print(help_result.output)
    assert 'Missing option "--bye-format"' in help_result.output
    assert help_result.exit_code == 2


def test_default_overrides_are_respected(cli_runner, unique_cli_env):
    help_result = cli_runner.invoke(idemseq.cli.cli, ['idemseq.examples.intuitive_interpretation', 'run', '--bye-format', 'Bye!', '--apples', '33'])
    assert '33 apples' in help_result.output
    assert help_result.exit_code == 0
