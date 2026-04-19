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


def test_check_passes(config_file: Path, env_file: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(env_file)])
    assert result.exit_code == 0, result.output


def test_check_fails_missing_key(config_file: Path, tmp_path: Path) -> None:
    bad_env = tmp_path / ".env"
    bad_env.write_text("DEBUG=true\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(bad_env)])
    assert result.exit_code == 1


def test_check_strict_fails_on_extra(config_file: Path, tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("APP_KEY=x\nUNKNOWN=y\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(env), "--strict"])
    assert result.exit_code == 1


def test_check_no_profiles_exits(tmp_path: Path, env_file: Path) -> None:
    cfg = tmp_path / "envcheck.toml"
    cfg.write_text("[profiles]\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--config", str(cfg), "--env-file", str(env_file)])
    assert result.exit_code == 2


def test_check_missing_env_file(config_file: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--config", str(config_file), "--env-file", str(tmp_path / "nope.env")])
    assert result.exit_code == 2
