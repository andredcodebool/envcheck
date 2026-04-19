"""Tests for envcheck.templater."""
import pytest

from envcheck.profile import Profile
from envcheck.templater import (
    template_from_keys,
    template_from_profile,
    write_template,
)


def _profile(name="svc", required=None, optional=None):
    return Profile(name=name, required=set(required or []), optional=set(optional or []))


def test_template_from_profile_header():
    p = _profile(required=["DB_URL"])
    out = template_from_profile(p)
    assert "profile: svc" in out


def test_template_from_profile_required_keys():
    p = _profile(required=["DB_URL", "APP_KEY"])
    out = template_from_profile(p)
    assert "DB_URL=your_value_here" in out
    assert "APP_KEY=your_value_here" in out


def test_template_from_profile_sensitive_redacted():
    p = _profile(required=["DB_PASSWORD"])
    out = template_from_profile(p)
    assert "DB_PASSWORD=****" in out


def test_template_from_profile_optional_commented():
    p = _profile(optional=["LOG_LEVEL"])
    out = template_from_profile(p)
    assert "# LOG_LEVEL=" in out


def test_template_from_profile_empty():
    p = _profile()
    out = template_from_profile(p)
    assert "profile: svc" in out


def test_template_from_keys_basic():
    out = template_from_keys(["HOST", "PORT"])
    assert "HOST=your_value_here" in out
    assert "PORT=your_value_here" in out


def test_template_from_keys_sorted():
    out = template_from_keys(["Z_KEY", "A_KEY"])
    assert out.index("A_KEY") < out.index("Z_KEY")


def test_template_from_keys_sensitive_redacted():
    out = template_from_keys(["API_TOKEN"])
    assert "****" in out


def test_template_from_keys_no_redact():
    out = template_from_keys(["API_TOKEN"], redact=False)
    assert "your_value_here" in out


def test_template_from_keys_empty():
    assert template_from_keys([]) == ""


def test_write_template(tmp_path):
    dest = tmp_path / ".env.example"
    write_template("FOO=bar\n", str(dest))
    assert dest.read_text() == "FOO=bar\n"
