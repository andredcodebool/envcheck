"""Tests for envcheck.cli_patch."""
import pytest
from click.testing import CliRunner
from envcheck.cli_patch import patch_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("ALPHA=1\nBETA=2\nGAMMA=3\n")
    return str(p)


def test_file_cmd_add_key(runner, env_file):
    result = runner.invoke(patch_group, ["file", env_file, "--set", "DELTA=4", "--quiet"])
    assert result.exit_code == 0
    assert "DELTA=4" in result.output


def test_file_cmd_update_key(runner, env_file):
    result = runner.invoke(patch_group, ["file", env_file, "--set", "ALPHA=99", "--quiet"])
    assert result.exit_code == 0
    assert "ALPHA=99" in result.output


def test_file_cmd_remove_key(runner, env_file):
    result = runner.invoke(patch_group, ["file", env_file, "--remove", "BETA", "--quiet"])
    assert result.exit_code == 0
    assert "BETA" not in result.output


def test_file_cmd_summary_on_stderr(runner, env_file):
    result = runner.invoke(
        patch_group,
        ["file", env_file, "--set", "NEW=x", "--remove", "ALPHA"],
        mix_stderr=False,
    )
    assert result.exit_code == 0
    assert "change(s)" in (result.stderr or "")


def test_file_cmd_write_output(runner, env_file, tmp_path):
    out = str(tmp_path / "out.env")
    result = runner.invoke(
        patch_group,
        ["file", env_file, "--set", "X=1", "--output", out, "--quiet"],
    )
    assert result.exit_code == 0
    content = open(out).read()
    assert "X=1" in content


def test_file_cmd_invalid_set_pair(runner, env_file):
    result = runner.invoke(patch_group, ["file", env_file, "--set", "NOEQUALS"])
    assert result.exit_code != 0


def test_file_cmd_preserves_untouched_keys(runner, env_file):
    result = runner.invoke(
        patch_group, ["file", env_file, "--set", "ALPHA=new", "--quiet"]
    )
    assert "BETA=2" in result.output
    assert "GAMMA=3" in result.output
