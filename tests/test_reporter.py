"""Tests for envcheck.reporter."""

from envcheck.checker import CheckResult
from envcheck.reporter import format_result, format_summary


def _make(ok: bool, missing=None, extra=None, service="svc"):
    return CheckResult(
        ok=ok,
        missing=missing or [],
        extra=extra or [],
        service=service,
    )


def test_format_result_ok_contains_ok():
    result = _make(ok=True)
    output = format_result(result, use_color=False)
    assert "OK" in output
    assert "[svc]" in output


def test_format_result_fail_shows_missing():
    result = _make(ok=False, missing=["SECRET_KEY", "DB_URL"])
    output = format_result(result, use_color=False)
    assert "FAIL" in output
    assert "SECRET_KEY" in output
    assert "DB_URL" in output


def test_format_result_shows_extra():
    result = _make(ok=False, extra=["UNUSED_VAR"])
    output = format_result(result, use_color=False)
    assert "UNUSED_VAR" in output
    assert "Extra" in output


def test_format_result_no_extra_section_when_empty():
    result = _make(ok=True)
    output = format_result(result, use_color=False)
    assert "Extra" not in output
    assert "Missing" not in output


def test_format_result_no_service_label():
    result = CheckResult(ok=True, missing=[], extra=[], service=None)
    output = format_result(result, use_color=False)
    assert "[env]" in output


def test_format_summary_all_pass():
    results = [_make(ok=True, service="a"), _make(ok=True, service="b")]
    output = format_summary(results, use_color=False)
    assert "2/2 passed" in output
    assert "all good" in output


def test_format_summary_some_fail():
    results = [
        _make(ok=True, service="a"),
        _make(ok=False, missing=["X"], service="b"),
    ]
    output = format_summary(results, use_color=False)
    assert "1/2 passed" in output
    assert "1 failed" in output


def test_format_summary_contains_individual_results():
    results = [_make(ok=False, missing=["TOKEN"], service="worker")]
    output = format_summary(results, use_color=False)
    assert "[worker]" in output
    assert "TOKEN" in output
