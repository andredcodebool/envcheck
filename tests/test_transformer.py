"""Tests for envcheck.transformer."""
import pytest
from envcheck.transformer import (
    filter_keys,
    merge_envs,
    prefix_keys,
    rename_keys,
    strip_prefix,
)

ENV = {"HOST": "localhost", "PORT": "5432", "PASSWORD": "secret"}


def test_rename_keys_basic():
    result = rename_keys(ENV, {"HOST": "DB_HOST", "PORT": "DB_PORT"})
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["PASSWORD"] == "secret"


def test_rename_keys_missing_source_skipped():
    result = rename_keys(ENV, {"MISSING": "NEW"})
    assert "NEW" not in result
    assert set(result.keys()) == set(ENV.keys())


def test_filter_keys_include():
    result = filter_keys(ENV, include=["HOST", "PORT"])
    assert set(result.keys()) == {"HOST", "PORT"}


def test_filter_keys_exclude():
    result = filter_keys(ENV, exclude=["PASSWORD"])
    assert "PASSWORD" not in result
    assert "HOST" in result


def test_filter_keys_include_and_exclude():
    result = filter_keys(ENV, include=["HOST", "PASSWORD"], exclude=["PASSWORD"])
    assert result == {"HOST": "localhost"}


def test_filter_keys_no_args_returns_copy():
    result = filter_keys(ENV)
    assert result == ENV
    assert result is not ENV


def test_merge_envs_last_wins():
    a = {"A": "1", "B": "2"}
    b = {"B": "99", "C": "3"}
    result = merge_envs(a, b, strategy="last")
    assert result == {"A": "1", "B": "99", "C": "3"}


def test_merge_envs_first_wins():
    a = {"A": "1", "B": "2"}
    b = {"B": "99", "C": "3"}
    result = merge_envs(a, b, strategy="first")
    assert result["B"] == "2"
    assert result["C"] == "3"


def test_merge_envs_invalid_strategy():
    with pytest.raises(ValueError, match="strategy"):
        merge_envs({}, strategy="unknown")


def test_prefix_keys():
    result = prefix_keys({"HOST": "x", "PORT": "y"}, "APP_")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_strip_prefix_matching():
    env = {"APP_HOST": "x", "APP_PORT": "y", "OTHER": "z"}
    result = strip_prefix(env, "APP_")
    assert result == {"HOST": "x", "PORT": "y", "OTHER": "z"}


def test_strip_prefix_no_match_passthrough():
    env = {"HOST": "x"}
    result = strip_prefix(env, "APP_")
    assert result == {"HOST": "x"}


def test_prefix_then_strip_roundtrip():
    prefixed = prefix_keys(ENV, "SVC_")
    restored = strip_prefix(prefixed, "SVC_")
    assert restored == ENV
