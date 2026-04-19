"""Tests for envcheck.comparator."""
import pytest
from envcheck.comparator import compare, format_compare, CompareReport
from envcheck.profile import Profile


PROFILE = Profile(
    name="web",
    required=["HOST", "PORT"],
    optional=["DEBUG"],
)

LEFT = {"HOST": "localhost", "PORT": "8000", "DEBUG": "true"}
RIGHT = {"HOST": "prod.example.com", "PORT": "443"}


def test_compare_returns_report():
    report = compare(LEFT, RIGHT, PROFILE)
    assert isinstance(report, CompareReport)
    assert report.profile_name == "web"


def test_compare_left_ok():
    report = compare(LEFT, RIGHT, PROFILE)
    assert report.left_result.ok is True


def test_compare_right_ok_when_required_present():
    report = compare(LEFT, RIGHT, PROFILE)
    assert report.right_result.ok is True


def test_compare_right_missing_required():
    right_bad = {"HOST": "prod.example.com"}
    report = compare(LEFT, right_bad, PROFILE)
    assert report.right_result.ok is False
    assert "PORT" in report.right_result.missing


def test_compare_diff_contains_changed():
    report = compare(LEFT, RIGHT, PROFILE)
    assert "HOST" in report.diff.changed or "PORT" in report.diff.changed


def test_compare_diff_added_key():
    report = compare(LEFT, RIGHT, PROFILE)
    # DEBUG present in left but not right -> removed from right perspective (added in left)
    assert "DEBUG" in report.diff.removed


def test_compare_labels():
    report = compare(LEFT, RIGHT, PROFILE, left_label="staging", right_label="prod")
    assert report.left_label == "staging"
    assert report.right_label == "prod"


def test_format_compare_contains_labels():
    report = compare(LEFT, RIGHT, PROFILE, left_label="staging", right_label="prod")
    out = format_compare(report, color=False)
    assert "staging" in out
    assert "prod" in out


def test_format_compare_contains_profile_name():
    report = compare(LEFT, RIGHT, PROFILE)
    out = format_compare(report, color=False)
    assert "web" in out


def test_format_compare_contains_diff_section():
    report = compare(LEFT, RIGHT, PROFILE)
    out = format_compare(report, color=False)
    assert "Diff" in out
