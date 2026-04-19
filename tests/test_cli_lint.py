"""Integration tests for cli_lint commands."""
import os
import pytest
from click.testing import CliRunner
from envcheck.cli_lint import lint_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def good_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DATABASE_URL=postgres://localhost/db\nPORT=8080\n")
    return str(p)


@pytest.fixture()
def bad_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("database_url=postgres://localhost/db\nEMPTY=\n")
    return str(p)


def test_file_cmd_clean_exits_zero(runner, good_env_file):
    result = runner.invoke(lint_group, ["file", good_env_file, "--no-color"])
    assert result.exit_code == 0
    assert "No lint issues" in result.output


def test_file_cmd_errors_exits_one(runner, bad_env_file):
    result = runner.invoke(lint_group, ["file", bad_env_file, "--no-color"])
    assert result.exit_code == 1
    assert "E001" in result.output


def test_file_cmd_warnings_only_exits_zero_by_default(runner, tmp_path):
    p = tmp_path / ".env"
    p.write_text("MY_KEY=\n")  # W003 only
    result = runner.invoke(lint_group, ["file", str(p), "--no-color"])
    assert result.exit_code == 0
    assert "W003" in result.output


def test_file_cmd_strict_exits_one_on_warning(runner, tmp_path):
    p = tmp_path / ".env"
    p.write_text("MY_KEY=\n")  # W003 only
    result = runner.invoke(lint_group, ["file", str(p), "--no-color", "--strict"])
    assert result.exit_code == 1


def test_env_cmd_runs(runner, monkeypatch):
    monkeypatch.setenv("GOOD_KEY", "value")
    result = runner.invoke(lint_group, ["env", "--no-color"])
    # Should not crash; exit code 0 or 1 depending on process env
    assert result.exit_code in (0, 1)


def test_file_cmd_missing_file(runner):
    result = runner.invoke(lint_group, ["file", "/nonexistent/.env"])
    assert result.exit_code != 0
