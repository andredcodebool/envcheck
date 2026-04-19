"""Tests for envcheck.redactor."""

import pytest
from envcheck.redactor import REDACTED, is_sensitive, redact, redact_string


# --- is_sensitive ---

def test_is_sensitive_password():
    assert is_sensitive("DB_PASSWORD") is True

def test_is_sensitive_token():
    assert is_sensitive("GITHUB_TOKEN") is True

def test_is_sensitive_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True

def test_is_sensitive_plain_key():
    assert is_sensitive("APP_PORT") is False

def test_is_sensitive_extra_pattern():
    assert is_sensitive("MY_CERT", extra_patterns=[r"(?i)cert"]) is True

def test_is_sensitive_extra_pattern_no_match():
    assert is_sensitive("APP_HOST", extra_patterns=[r"(?i)cert"]) is False


# --- redact ---

def test_redact_replaces_sensitive():
    env = {"DB_PASSWORD": "s3cr3t", "APP_PORT": "8080"}
    result = redact(env)
    assert result["DB_PASSWORD"] == REDACTED
    assert result["APP_PORT"] == "8080"

def test_redact_does_not_mutate_original():
    env = {"SECRET": "abc"}
    redact(env)
    assert env["SECRET"] == "abc"

def test_redact_custom_redact_value():
    env = {"API_KEY": "xyz"}
    result = redact(env, redact_value="<hidden>")
    assert result["API_KEY"] == "<hidden>"

def test_redact_empty_env():
    assert redact({}) == {}


# --- redact_string ---

def test_redact_string_basic():
    raw = "APP_PORT=8080\nDB_PASSWORD=secret\n"
    out = redact_string(raw)
    assert "secret" not in out
    assert REDACTED in out
    assert "APP_PORT=8080" in out

def test_redact_string_preserves_comments():
    raw = "# comment\nTOKEN=abc"
    out = redact_string(raw)
    assert "# comment" in out
    assert "abc" not in out

def test_redact_string_blank_lines_preserved():
    raw = "A=1\n\nB=2"
    out = redact_string(raw)
    lines = out.split("\n")
    assert "" in lines

def test_redact_string_no_sensitive():
    raw = "HOST=localhost\nPORT=5432"
    out = redact_string(raw)
    assert out == raw
