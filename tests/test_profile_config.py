"""Tests for envcheck.profile and envcheck.config."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envcheck.profile import Profile, load_profiles, profile_from_dict
from envcheck.config import ConfigError, find_config, get_profiles


# ---------------------------------------------------------------------------
# profile tests
# ---------------------------------------------------------------------------

def test_profile_from_dict_basic():
    p = profile_from_dict({"name": "web", "required": ["PORT", "HOST"]})
    assert p.name == "web"
    assert p.required == ["PORT", "HOST"]
    assert p.optional == []


def test_profile_all_known():
    p = Profile(name="db", required=["DB_URL"], optional=["DB_POOL"])
    assert set(p.all_known()) == {"DB_URL", "DB_POOL"}


def test_load_profiles_keyed_by_name():
    data = [
        {"name": "web", "required": ["PORT"]},
        {"name": "worker", "required": ["QUEUE_URL"]},
    ]
    profiles = load_profiles(data)
    assert set(profiles.keys()) == {"web", "worker"}


# ---------------------------------------------------------------------------
# config tests
# ---------------------------------------------------------------------------

def _write_config(path: Path, content: str) -> Path:
    cfg = path / "envcheck.toml"
    cfg.write_text(textwrap.dedent(content))
    return cfg


def test_find_config(tmp_path):
    cfg = _write_config(tmp_path, "")
    assert find_config(tmp_path) == cfg


def test_find_config_not_found(tmp_path):
    assert find_config(tmp_path / "deep" / "nested") is None


def test_get_profiles(tmp_path):
    _write_config(tmp_path, """
        [[profiles]]
        name = "api"
        required = ["SECRET_KEY", "DATABASE_URL"]
        optional = ["DEBUG"]
    """)
    profiles = get_profiles(tmp_path / "envcheck.toml")
    assert "api" in profiles
    assert profiles["api"].required == ["SECRET_KEY", "DATABASE_URL"]


def test_get_profiles_missing_section_raises(tmp_path):
    cfg = tmp_path / "envcheck.toml"
    cfg.write_text("[tool]\nname = 'envcheck'\n")
    with pytest.raises(ConfigError, match="profiles"):
        get_profiles(cfg)
