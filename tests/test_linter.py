"""Tests for envcheck.linter."""
import pytest
from envcheck.linter import lint_env, format_lint, LintIssue


def test_clean_env_ok():
    report = lint_env({"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"})
    assert report.ok


def test_lowercase_key_flagged():
    report = lint_env({"database_url": "x"})
    codes = [i.code for i in report.issues]
    assert "E001" in codes


def test_mixed_case_key_flagged():
    report = lint_env({"DatabaseUrl": "x"})
    codes = [i.code for i in report.issues]
    assert "E001" in codes


def test_leading_digit_key_flagged():
    report = lint_env({"1BAD": "x"})
    codes = [i.code for i in report.issues]
    assert "E002" in codes


def test_double_underscore_warns():
    report = lint_env({"MY__KEY": "val"})
    codes = [i.code for i in report.issues]
    assert "W001" in codes


def test_leading_whitespace_value_warns():
    report = lint_env({"MY_KEY": " value"})
    codes = [i.code for i in report.issues]
    assert "W002" in codes


def test_trailing_whitespace_value_warns():
    report = lint_env({"MY_KEY": "value "})
    codes = [i.code for i in report.issues]
    assert "W002" in codes


def test_empty_value_warns():
    report = lint_env({"MY_KEY": ""})
    codes = [i.code for i in report.issues]
    assert "W003" in codes


def test_format_lint_ok_no_color():
    report = lint_env({"GOOD": "val"})
    out = format_lint(report, color=False)
    assert "No lint issues" in out


def test_format_lint_errors_no_color():
    report = lint_env({"bad_key": ""})
    out = format_lint(report, color=False)
    assert "E001" in out
    assert "W003" in out


def test_format_lint_color_contains_ansi():
    report = lint_env({"bad": ""})
    out = format_lint(report, color=True)
    assert "\033[" in out


def test_multiple_issues_multiple_lines():
    report = lint_env({"bad__key": " "})
    out = format_lint(report, color=False)
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) >= 2
