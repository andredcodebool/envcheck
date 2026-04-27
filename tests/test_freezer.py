"""Tests for envcheck.freezer and envcheck.cli_freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envcheck.freezer import FreezeError, freeze, list_freezes, thaw, write_env_file
from envcheck.cli_freeze import freeze_group


# ---------------------------------------------------------------------------
# freezer unit tests
# ---------------------------------------------------------------------------

def test_freeze_creates_file(tmp_path):
    env = {"FOO": "bar", "BAZ": "qux"}
    out = freeze(env, "test", tmp_path)
    assert out.exists()
    assert out.name == "test.freeze.json"


def test_freeze_content_roundtrip(tmp_path):
    env = {"ALPHA": "1", "BETA": "2"}
    out = freeze(env, "snap", tmp_path)
    payload = json.loads(out.read_text())
    assert payload["name"] == "snap"
    assert payload["env"] == env
    assert payload["keys"] == sorted(env.keys())


def test_thaw_returns_record(tmp_path):
    env = {"X": "10"}
    freeze(env, "r1", tmp_path)
    record = thaw(tmp_path / "r1.freeze.json")
    assert record.name == "r1"
    assert record.env == env


def test_thaw_missing_file_raises(tmp_path):
    with pytest.raises(FreezeError, match="not found"):
        thaw(tmp_path / "ghost.freeze.json")


def test_thaw_invalid_json_raises(tmp_path):
    bad = tmp_path / "bad.freeze.json"
    bad.write_text("not json")
    with pytest.raises(FreezeError, match="invalid"):
        thaw(bad)


def test_list_freezes_empty(tmp_path):
    assert list_freezes(tmp_path) == []


def test_list_freezes_sorted(tmp_path):
    for name in ("c", "a", "b"):
        freeze({"K": "v"}, name, tmp_path)
    names = [f.stem.replace(".freeze", "") for f in list_freezes(tmp_path)]
    assert names == ["a", "b", "c"]


def test_write_env_file(tmp_path):
    from envcheck.freezer import FreezeRecord
    record = FreezeRecord(name="x", env={"FOO": "1", "BAR": "2"})
    dest = tmp_path / "out.env"
    write_env_file(record, dest)
    content = dest.read_text()
    assert "BAR=2" in content
    assert "FOO=1" in content


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_save_and_list(runner, tmp_path):
    env_content = "KEY1=hello\nKEY2=world\n"
    env_file = tmp_path / "sample.env"
    env_file.write_text(env_content)
    result = runner.invoke(
        freeze_group,
        ["save", "--name", "mysave", "--file", str(env_file), "--dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert "2 keys" in result.output

    result2 = runner.invoke(freeze_group, ["list", "--dir", str(tmp_path)])
    assert result2.exit_code == 0
    assert "mysave.freeze.json" in result2.output


def test_cli_thaw_stdout(runner, tmp_path):
    freeze({"ENV_A": "alpha"}, "t1", tmp_path)
    result = runner.invoke(freeze_group, ["thaw", "t1", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "ENV_A=alpha" in result.output


def test_cli_thaw_to_file(runner, tmp_path):
    freeze({"Z": "26"}, "t2", tmp_path)
    out_file = tmp_path / "result.env"
    result = runner.invoke(
        freeze_group,
        ["thaw", "t2", "--dir", str(tmp_path), "--output", str(out_file)],
    )
    assert result.exit_code == 0
    assert out_file.exists()
    assert "Z=26" in out_file.read_text()


def test_cli_thaw_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(freeze_group, ["thaw", "nope", "--dir", str(tmp_path)])
    assert result.exit_code != 0
