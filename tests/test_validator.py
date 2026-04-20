"""Tests for envcheck.validator."""
import pytest
from envcheck.validator import (
    validate,
    format_validation,
    ValidationIssue,
    ValidationReport,
)


ENV = {
    "PORT": "8080",
    "DEBUG": "true",
    "BASE_URL": "https://example.com",
    "EMPTY_VAR": "",
    "NOT_AN_INT": "abc",
    "BAD_URL": "ftp://nope.com",
    "BAD_BOOL": "maybe",
}


def test_validate_integer_ok():
    report = validate({"PORT": "8080"}, {"PORT": ["integer"]})
    assert report.ok


def test_validate_integer_fail():
    report = validate({"PORT": "abc"}, {"PORT": ["integer"]})
    assert not report.ok
    assert report.issues[0].rule == "integer"
    assert report.issues[0].key == "PORT"


def test_validate_boolean_ok():
    for val in ["true", "false", "1", "0", "yes", "no", "True", "YES"]:
        report = validate({"DEBUG": val}, {"DEBUG": ["boolean"]})
        assert report.ok, f"expected ok for value {val!r}"


def test_validate_boolean_fail():
    report = validate({"DEBUG": "maybe"}, {"DEBUG": ["boolean"]})
    assert not report.ok
    assert report.issues[0].rule == "boolean"


def test_validate_url_ok():
    report = validate({"BASE_URL": "https://example.com"}, {"BASE_URL": ["url"]})
    assert report.ok


def test_validate_url_fail():
    report = validate({"BASE_URL": "ftp://nope.com"}, {"BASE_URL": ["url"]})
    assert not report.ok
    assert report.issues[0].rule == "url"


def test_validate_nonempty_ok():
    report = validate({"NAME": "alice"}, {"NAME": ["nonempty"]})
    assert report.ok


def test_validate_nonempty_fail():
    report = validate({"NAME": "   "}, {"NAME": ["nonempty"]})
    assert not report.ok
    assert report.issues[0].rule == "nonempty"


def test_missing_key_skipped():
    """Keys not present in env are silently skipped."""
    report = validate({}, {"MISSING": ["integer", "nonempty"]})
    assert report.ok


def test_unknown_rule_skipped():
    report = validate({"X": "val"}, {"X": ["nonexistent_rule"]})
    assert report.ok


def test_multiple_rules_multiple_failures():
    report = validate({"X": ""}, {"X": ["nonempty", "integer"]})
    assert len(report.issues) == 2


def test_extra_rules_applied():
    def must_start_with_prod(key, value):
        if not value.startswith("prod"):
            from envcheck.validator import ValidationIssue
            return ValidationIssue(key, value, "prod_prefix", "must start with 'prod'")
        return None

    report = validate(
        {"ENV_NAME": "staging"},
        {"ENV_NAME": ["prod_prefix"]},
        extra_rules={"prod_prefix": must_start_with_prod},
    )
    assert not report.ok
    assert report.issues[0].rule == "prod_prefix"


def test_format_validation_ok():
    report = ValidationReport()
    out = format_validation(report)
    assert "passed" in out


def test_format_validation_fail():
    report = validate({"PORT": "bad"}, {"PORT": ["integer"]})
    out = format_validation(report)
    assert "failed" in out
    assert "PORT" in out
    assert "integer" in out
