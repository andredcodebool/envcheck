"""Integration tests for the compare CLI sub-commands."""
import os
import pytest
from click.testing import CliRunner
from envcheck.cli_compare import compare_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def two_env_files(tmp_path):
    left = tmp_path / "left.env"
    right = tmp_path / "right.env"
    left.write_text("HOST=localhost\nPORT=8000\nDEBUG=true\n")
    right.write_text("HOST=prod.example.com\nPORT=443\n")
    return str(left), str(right)


@pytest.fixture()
def config_file(tmp_path):
    cfg = tmp_path / "envcheck.toml"
    cfg.write_text(
        '[profiles.web]\nrequired = ["HOST", "PORT"]\noptional = ["DEBUG"]\n'
    )
    return str(cfg)


def test_files_cmd_passes(runner, two_env_files, config_file):
    left, right = two_env_files
    result = runner.invoke(
        compare_group, ["files", left, right, "--config", config_file, "--profile", "web", "--no-color"]
    )
    assert result.exit_code == 0


def test_files_cmd_shows_both_labels(runner, two_env_files, config_file):
    left, right = two_env_files
    result = runner.invoke(
        compare_group, ["files", left, right, "--config", config_file, "--no-color"]
    )
    assert left in result.output or "left" in result.output


def test_files_cmd_fails_on_missing_required(runner, tmp_path, config_file):
    left = tmp_path / "a.env"
    right = tmp_path / "b.env"
    left.write_text("HOST=a\n")
    right.write_text("HOST=b\n")
    result = runner.invoke(
        compare_group,
        ["files", str(left), str(right), "--config", config_file, "--profile", "web", "--no-color"],
    )
    assert result.exit_code != 0


def test_files_cmd_diff_section_present(runner, two_env_files, config_file):
    left, right = two_env_files
    result = runner.invoke(
        compare_group, ["files", left, right, "--config", config_file, "--no-color"]
    )
    assert "Diff" in result.output


def test_env_vs_file_cmd(runner, tmp_path, config_file, monkeypatch):
    monkeypatch.setenv("HOST", "live-host")
    monkeypatch.setenv("PORT", "9000")
    env_file = tmp_path / "ref.env"
    env_file.write_text("HOST=ref-host\nPORT=80\n")
    result = runner.invoke(
        compare_group,
        ["env-vs-file", str(env_file), "--config", config_file, "--profile", "web", "--no-color"],
    )
    assert "live" in result.output
