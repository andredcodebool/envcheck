"""Tests for envcheck.loader."""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from envcheck.loader import (
    LoadError,
    load_from_dir,
    load_from_env,
    load_from_file,
    load_from_string,
)


def test_load_from_string_basic():
    raw = "FOO=bar\nBAZ=qux\n"
    assert load_from_string(raw) == {"FOO": "bar", "BAZ": "qux"}


def test_load_from_file(tmp_path):
    f = tmp_path / "service.env"
    f.write_text("HOST=localhost\nPORT=5432\n")
    assert load_from_file(f) == {"HOST": "localhost", "PORT": "5432"}


def test_load_from_file_missing_raises(tmp_path):
    with pytest.raises(LoadError, match="not found"):
        load_from_file(tmp_path / "ghost.env")


def test_load_from_file_directory_raises(tmp_path):
    with pytest.raises(LoadError, match="Not a file"):
        load_from_file(tmp_path)


def test_load_from_dir(tmp_path):
    (tmp_path / "a.env").write_text("A=1\n")
    (tmp_path / "b.env").write_text("B=2\n")
    result = load_from_dir(tmp_path)
    assert result == {"a.env": {"A": "1"}, "b.env": {"B": "2"}}


def test_load_from_dir_empty(tmp_path):
    assert load_from_dir(tmp_path) == {}


def test_load_from_dir_not_dir_raises(tmp_path):
    f = tmp_path / "x.env"
    f.write_text("")
    with pytest.raises(LoadError):
        load_from_dir(f)


def test_load_from_env_no_prefix(monkeypatch):
    monkeypatch.setenv("_TEST_VAR", "hello")
    env = load_from_env()
    assert env["_TEST_VAR"] == "hello"


def test_load_from_env_with_prefix(monkeypatch):
    monkeypatch.setenv("MYAPP_DB", "postgres")
    monkeypatch.setenv("MYAPP_PORT", "5432")
    monkeypatch.setenv("OTHER_VAR", "ignore")
    result = load_from_env(prefix="MYAPP_")
    assert result == {"DB": "postgres", "PORT": "5432"}
