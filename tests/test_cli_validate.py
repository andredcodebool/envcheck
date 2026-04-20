"""Integration tests for the validate CLI commands."""
import json
import os
import pytest
from click.testing import CliRunner
from envcheck.cli_validate import validate_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("PORT=8080\nDEBUG=true\nBASE_URL=https://example.com\n")
    return str(p)


@pytest.fixture()
def bad_env_file(tmp_path):
    p = tmp_path / ".env.bad"
    p.write_text("PORT=notanint\nDEBUG=maybe\nBASE_URL=ftp://bad\n")
    return str(p)


@pytest.fixture()
def rules_file(tmp_path):
    rules = {
        "PORT": ["integer", "nonempty"],
        "DEBUG": ["boolean"],
        "BASE_URL": ["url"],
    }
    p = tmp_path / "rules.json"
    p.write_text(json.dumps(rules))
    return str(p)


def test_file_cmd_passes(runner, env_file, rules_file):
    result = runner.invoke(validate_group, ["file", env_file, "--rules", rules_file])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_file_cmd_quiet_no_output_on_pass(runner, env_file, rules_file):
    result = runner.invoke(validate_group, ["file", env_file, "--rules", rules_file, "--quiet"])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_file_cmd_fails_on_bad_values(runner, bad_env_file, rules_file):
    result = runner.invoke(validate_group, ["file", bad_env_file, "--rules", rules_file])
    assert result.exit_code == 1
    assert "failed" in result.output
    assert "PORT" in result.output
    assert "DEBUG" in result.output
    assert "BASE_URL" in result.output


def test_file_cmd_shows_rule_names(runner, bad_env_file, rules_file):
    result = runner.invoke(validate_group, ["file", bad_env_file, "--rules", rules_file])
    assert "integer" in result.output
    assert "boolean" in result.output
    assert "url" in result.output


def test_file_cmd_missing_env_file(runner, rules_file):
    result = runner.invoke(validate_group, ["file", "/nonexistent/.env", "--rules", rules_file])
    assert result.exit_code != 0


def test_file_cmd_invalid_rules_json(runner, env_file, tmp_path):
    bad_rules = tmp_path / "bad.json"
    bad_rules.write_text("not valid json{{{")
    result = runner.invoke(validate_group, ["file", env_file, "--rules", str(bad_rules)])
    assert result.exit_code == 2
