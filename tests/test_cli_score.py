"""Tests for envcheck.cli_score."""
from __future__ import annotations

import json
import textwrap

import pytest
from click.testing import CliRunner

from envcheck.cli_score import score_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=8080\nDEBUG=false\n")
    return str(p)


@pytest.fixture()
def messy_env_file(tmp_path):
    p = tmp_path / ".env"
    # lowercase key triggers lint error
    p.write_text("host=localhost\nPORT=8080\n")
    return str(p)


def test_file_cmd_clean_exits_zero(runner, clean_env_file):
    result = runner.invoke(score_group, ["file", clean_env_file])
    assert result.exit_code == 0
    assert "Health Score" in result.output


def test_file_cmd_shows_grade(runner, clean_env_file):
    result = runner.invoke(score_group, ["file", clean_env_file])
    assert "[" in result.output  # grade bracket


def test_file_cmd_lint_deduction(runner, messy_env_file):
    result = runner.invoke(score_group, ["file", messy_env_file])
    # lowercase key is a lint error → deduction shown
    assert "Deductions" in result.output or "lint" in result.output.lower()


def test_file_cmd_json_output(runner, clean_env_file):
    result = runner.invoke(score_group, ["file", clean_env_file, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "score" in data
    assert "grade" in data
    assert "deductions" in data


def test_file_cmd_json_perfect_score(runner, clean_env_file):
    result = runner.invoke(score_group, ["file", clean_env_file, "--json"])
    data = json.loads(result.output)
    assert data["score"] == data["total"]
    assert data["grade"] == "A"


def test_file_cmd_bad_profile_exits_two(runner, clean_env_file, tmp_path):
    cfg = tmp_path / "envcheck.toml"
    cfg.write_text(textwrap.dedent("""\
        [profiles.default]
        required = ["HOST"]
    """))
    result = runner.invoke(
        score_group,
        ["file", clean_env_file, "--profile", "nonexistent", "--config", str(cfg)],
    )
    assert result.exit_code == 2
