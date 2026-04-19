"""Tests for envcheck.cli_interpolate."""
import pytest
from click.testing import CliRunner
from envcheck.cli_interpolate import interpolate_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("BASE=/opt\nFULL=${BASE}/app\nNAME=service\n")
    return str(p)


@pytest.fixture()
def missing_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FULL=${BASE}/app\n")
    return str(p)


def test_resolve_outputs_interpolated(runner, env_file):
    result = runner.invoke(interpolate_group, ["resolve", env_file])
    assert result.exit_code == 0
    assert "FULL=/opt/app" in result.output


def test_resolve_non_strict_leaves_missing(runner, missing_env_file):
    result = runner.invoke(interpolate_group, ["resolve", missing_env_file])
    assert result.exit_code == 0
    assert "${BASE}" in result.output


def test_resolve_strict_exits_one_on_missing(runner, missing_env_file):
    result = runner.invoke(interpolate_group, ["resolve", "--strict", missing_env_file])
    assert result.exit_code == 1
    assert "Interpolation error" in result.output


def test_show_missing_reports_refs(runner, missing_env_file):
    result = runner.invoke(interpolate_group, ["resolve", "--show-missing", missing_env_file])
    assert result.exit_code == 1
    assert "BASE" in result.output


def test_show_missing_clean_exits_zero(runner, env_file):
    result = runner.invoke(interpolate_group, ["resolve", "--show-missing", env_file])
    assert result.exit_code == 0
    assert "No unresolved" in result.output


def test_check_refs_clean(runner, env_file):
    result = runner.invoke(interpolate_group, ["check-refs", env_file])
    assert result.exit_code == 0
    assert "resolved" in result.output


def test_check_refs_reports_missing(runner, missing_env_file):
    result = runner.invoke(interpolate_group, ["check-refs", missing_env_file])
    assert result.exit_code == 1
    assert "BASE" in result.output
