"""Tests for the CLI layer."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envcheck.cli import cli


MINIMAL_CONFIG = """
[profiles.default]
required = ["APP_KEY"]
optional = ["DEBUG"]
"""


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    p = tmp_path / "envcheck.toml"
    p.write_text(MINIMAL_CONFIG)
    return p


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("APP_KEY=secret\nDEBUG=true\n")
    return p


@pytest.fixture()
def runner() -> CliRunner:
    """Return a shared CliRunner instance for all tests."""
    return CliRunner()


def test_check_passes(config_file: Path, env_file: Path, runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(env_file)])
    assert result.exit_code == 0, result.output


def test_check_fails_missing_key(config_file: Path, tmp_path: Path, runner: CliRunner) -> None:
    bad_env = tmp_path / ".env"
    bad_env.write_text("DEBUG=true\n")
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(bad_env)])
    assert result.exit_code == 1


def test_check_strict_fails_on_extra(config_file: Path, tmp_path: Path, runner: CliRunner) -> None:
    env = tmp_path / ".env"
    env.write_text("APP_KEY=x\nUNKNOWN=y\n")
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(env), "--strict"])
    assert result.exit_code == 1


def test_check_no_profiles_exits(tmp_path: Path, env_file: Path, runner: CliRunner) -> None:
    cfg = tmp_path / "envcheck.toml"
    cfg.write_text("[profiles]\n")
    result = runner.invoke(cli, ["check", "--config", str(cfg), "--env-file", str(env_file)])
    assert result.exit_code == 2


def test_check_missing_env_file(config_file: Path, tmp_path: Path, runner: CliRunner) -> None:
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(tmp_path / "nope.env")])
    assert result.exit_code == 2


def test_check_missing_config_file(tmp_path: Path, env_file: Path, runner: CliRunner) -> None:
    """Invoking check with a non-existent config file should exit with code 2."""
    result = runner.invoke(cli, ["check", "--config", str(tmp_path / "missing.toml"), "--env-file", str(env_file)])
    assert result.exit_code == 2
