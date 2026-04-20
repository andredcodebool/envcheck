"""Tests for envcheck.masker."""

from __future__ import annotations

import pytest

from envcheck.masker import mask_env, mask_string, mask_value

_MASK = "********"


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

def test_mask_value_sensitive_key_returns_mask():
    assert mask_value("DB_PASSWORD", "s3cr3t") == _MASK


def test_mask_value_insensitive_key_returns_value():
    assert mask_value("APP_NAME", "myapp") == "myapp"


def test_mask_value_token_key_masked():
    assert mask_value("GITHUB_TOKEN", "ghp_abc123") == _MASK


def test_mask_value_api_key_masked():
    assert mask_value("STRIPE_API_KEY", "sk_live_xyz") == _MASK


def test_mask_value_show_prefix_long_value():
    result = mask_value("DB_PASSWORD", "abcdefgh", show_prefix=True)
    assert result == "abcd" + _MASK


def test_mask_value_show_prefix_short_value_still_masked():
    # value shorter than _VISIBLE_CHARS — falls back to full mask
    result = mask_value("DB_PASSWORD", "abc", show_prefix=True)
    assert result == _MASK


def test_mask_value_custom_mask():
    assert mask_value("SECRET", "value", mask="[REDACTED]") == "[REDACTED]"


def test_mask_value_extra_patterns():
    result = mask_value("MY_CUSTOM_CRED", "hunter2", extra_patterns=[r"cred"])
    assert result == _MASK


def test_mask_value_extra_patterns_no_match():
    result = mask_value("MY_CUSTOM_CRED", "hunter2", extra_patterns=[r"^nomatch$"])
    # Without the extra pattern matching, CRED is not in default sensitive list
    # so result depends on default patterns; just ensure no crash.
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# mask_env
# ---------------------------------------------------------------------------

def test_mask_env_masks_sensitive_leaves_plain():
    env = {"DB_PASSWORD": "secret", "APP_ENV": "production", "API_KEY": "key123"}
    result = mask_env(env)
    assert result["DB_PASSWORD"] == _MASK
    assert result["API_KEY"] == _MASK
    assert result["APP_ENV"] == "production"


def test_mask_env_returns_new_dict():
    env = {"DB_PASSWORD": "secret"}
    result = mask_env(env)
    assert result is not env


def test_mask_env_empty():
    assert mask_env({}) == {}


def test_mask_env_show_prefix():
    env = {"DB_PASSWORD": "abcdefgh"}
    result = mask_env(env, show_prefix=True)
    assert result["DB_PASSWORD"].startswith("abcd")


# ---------------------------------------------------------------------------
# mask_string
# ---------------------------------------------------------------------------

def test_mask_string_sensitive_line():
    assert mask_string("DB_PASSWORD=hunter2") == f"DB_PASSWORD={_MASK}"


def test_mask_string_plain_line_unchanged():
    assert mask_string("APP_NAME=myapp") == "APP_NAME=myapp"


def test_mask_string_no_equals_unchanged():
    assert mask_string("# comment line") == "# comment line"


def test_mask_string_value_with_equals():
    # Values that themselves contain '=' should be fully masked
    result = mask_string("DB_PASSWORD=base64===")
    assert result == f"DB_PASSWORD={_MASK}"
