"""Tests for envcheck.scorer."""
from __future__ import annotations

import pytest

from envcheck.checker import CheckResult
from envcheck.linter import LintIssue, LintReport
from envcheck.scorer import ScoreReport, format_score, score_env
from envcheck.validator import ValidationIssue, ValidationReport


def _check(missing=(), extra=()) -> CheckResult:
    return CheckResult(ok=not missing, missing=list(missing), extra=list(extra))


def _lint(*issues) -> LintReport:
    return LintReport(ok=not issues, issues=list(issues))


def _lint_issue(key, msg, severity="error") -> LintIssue:
    return LintIssue(key=key, message=msg, severity=severity)


def _val_issue(key, rule, passed, msg="") -> ValidationIssue:
    return ValidationIssue(key=key, rule=rule, passed=passed, message=msg)


def _validation(*issues) -> ValidationReport:
    failed = [i for i in issues if not i.passed]
    return ValidationReport(ok=not failed, issues=list(issues))


# --- ScoreReport ---

def test_score_no_deductions():
    r = ScoreReport(total=100, passed=100)
    assert r.score == 100
    assert r.grade == "A"


def test_score_with_deductions():
    r = ScoreReport(total=100, passed=80, deductions=[("missing key", 10), ("lint error", 10)])
    assert r.score == 80


def test_score_floor_zero():
    r = ScoreReport(total=100, passed=0, deductions=[("lots of issues", 200)])
    assert r.score == 0


def test_grade_boundaries():
    assert ScoreReport(total=100, passed=100).grade == "A"
    assert ScoreReport(total=100, passed=75).grade == "B"
    assert ScoreReport(total=100, passed=60).grade == "C"
    assert ScoreReport(total=100, passed=40).grade == "D"
    assert ScoreReport(total=100, passed=20).grade == "F"


# --- score_env ---

def test_perfect_score():
    r = score_env(check=_check(), lint=_lint(), validation=_validation())
    assert r.score == 100
    assert r.deductions == []


def test_missing_keys_deduct():
    r = score_env(check=_check(missing=["A", "B"]))
    assert r.score == 80
    assert any("missing" in reason for reason, _ in r.deductions)


def test_lint_errors_deduct():
    issues = [_lint_issue("bad_key", "lowercase", "error")]
    r = score_env(lint=_lint(*issues))
    assert r.score == 95


def test_lint_warnings_deduct_less():
    issues = [_lint_issue("key", "double underscore", "warning")]
    r = score_env(lint=_lint(*issues))
    assert r.score == 98


def test_validation_failures_deduct():
    issues = [_val_issue("PORT", "integer", False, "not an int")]
    r = score_env(validation=_validation(*issues))
    assert r.score == 92


def test_combined_deductions():
    r = score_env(
        check=_check(missing=["SECRET"]),
        lint=_lint(_lint_issue("bad", "msg", "error")),
        validation=_validation(_val_issue("PORT", "integer", False)),
    )
    assert r.score == 100 - 10 - 5 - 8


# --- format_score ---

def test_format_score_perfect():
    r = score_env()
    out = format_score(r)
    assert "100/100" in out
    assert "perfect" in out.lower()


def test_format_score_shows_deductions():
    r = score_env(check=_check(missing=["KEY"]))
    out = format_score(r)
    assert "Deductions" in out
    assert "-10" in out
