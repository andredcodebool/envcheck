"""Tests for envcheck.normalizer."""
import pytest

from envcheck.normalizer import (
    NormalizeReport,
    format_normalize,
    normalize,
    normalize_keys,
    normalize_values,
)


# ---------------------------------------------------------------------------
# normalize_keys
# ---------------------------------------------------------------------------

def test_normalize_keys_uppercase():
    report = normalize_keys({"db_host": "localhost"})
    assert "DB_HOST" in report.normalized
    assert report.normalized["DB_HOST"] == "localhost"


def test_normalize_keys_records_change():
    report = normalize_keys({"db_host": "localhost"})
    assert len(report.changes) == 1
    kind, old, new = report.changes[0]
    assert kind == "key"
    assert old == "db_host"
    assert new == "DB_HOST"


def test_normalize_keys_already_upper_no_change():
    report = normalize_keys({"DB_HOST": "localhost"})
    assert report.changes == []


def test_normalize_keys_hyphen_to_underscore():
    report = normalize_keys({"my-key": "val"})
    assert "MY_KEY" in report.normalized


def test_normalize_keys_does_not_mutate_input():
    original = {"lower": "v"}
    normalize_keys(original)
    assert "lower" in original


# ---------------------------------------------------------------------------
# normalize_values
# ---------------------------------------------------------------------------

def test_normalize_values_strips_whitespace():
    report = normalize_values({"KEY": "  hello  "})
    assert report.normalized["KEY"] == "hello"


def test_normalize_values_records_change():
    report = normalize_values({"KEY": " val "})
    assert len(report.changes) == 1
    kind, key, new_val = report.changes[0]
    assert kind == "value"
    assert key == "KEY"
    assert new_val == "val"


def test_normalize_values_clean_no_change():
    report = normalize_values({"KEY": "clean"})
    assert report.changes == []


# ---------------------------------------------------------------------------
# normalize (combined)
# ---------------------------------------------------------------------------

def test_normalize_combined_changes():
    env = {"my_key": "  value  "}
    report = normalize(env)
    assert "MY_KEY" in report.normalized
    assert report.normalized["MY_KEY"] == "value"
    assert len(report.changes) == 2


def test_normalize_no_changes():
    report = normalize({"KEY": "value"})
    assert report.changes == []
    assert report.normalized == {"KEY": "value"}


def test_normalize_preserves_original():
    env = {"lower": " v "}
    report = normalize(env)
    assert report.original == {"lower": " v "}


# ---------------------------------------------------------------------------
# format_normalize
# ---------------------------------------------------------------------------

def test_format_normalize_no_changes():
    report = normalize({"KEY": "val"})
    assert format_normalize(report) == "No changes."


def test_format_normalize_shows_key_change():
    report = normalize_keys({"lower": "v"})
    output = format_normalize(report)
    assert "lower" in output
    assert "LOWER" in output


def test_format_normalize_shows_value_change():
    report = normalize_values({"KEY": " v "})
    output = format_normalize(report)
    assert "KEY" in output
    assert "stripped" in output
