"""Tests for envcheck.duplicates."""

import pytest

from envcheck.duplicates import (
    DuplicateReport,
    find_intra_duplicates,
    find_inter_duplicates,
    scan,
    format_report,
)


# ---------------------------------------------------------------------------
# find_intra_duplicates
# ---------------------------------------------------------------------------

def test_intra_no_duplicates():
    lines = ["FOO=1", "BAR=2"]
    assert find_intra_duplicates(lines) == {}


def test_intra_single_duplicate():
    lines = ["FOO=1", "BAR=2", "FOO=3"]
    result = find_intra_duplicates(lines)
    assert result == {"FOO": 2}


def test_intra_triple_occurrence():
    lines = ["X=a", "X=b", "X=c"]
    assert find_intra_duplicates(lines)["X"] == 3


def test_intra_ignores_comments_and_blanks():
    lines = ["# FOO=1", "", "FOO=1", "BAR=2"]
    assert find_intra_duplicates(lines) == {}


def test_intra_ignores_lines_without_equals():
    lines = ["NOEQUALS", "FOO=1"]
    assert find_intra_duplicates(lines) == {}


# ---------------------------------------------------------------------------
# find_inter_duplicates
# ---------------------------------------------------------------------------

def test_inter_no_overlap():
    envs = [{"A": "1"}, {"B": "2"}]
    assert find_inter_duplicates(envs) == []


def test_inter_single_overlap():
    envs = [{"A": "1", "B": "2"}, {"B": "3", "C": "4"}]
    assert find_inter_duplicates(envs) == ["B"]


def test_inter_multiple_overlaps_sorted():
    envs = [{"Z": "1", "A": "2"}, {"Z": "3", "A": "4"}]
    assert find_inter_duplicates(envs) == ["A", "Z"]


def test_inter_three_sources():
    envs = [{"X": "1"}, {"X": "2"}, {"X": "3"}]
    assert find_inter_duplicates(envs) == ["X"]


# ---------------------------------------------------------------------------
# scan + DuplicateReport
# ---------------------------------------------------------------------------

def test_scan_no_duplicates():
    report = scan(lines=["A=1", "B=2"], envs=[{"A": "1"}, {"B": "2"}])
    assert not report.has_duplicates


def test_scan_intra_only():
    report = scan(lines=["A=1", "A=2"])
    assert report.has_duplicates
    assert "A" in report.intra


def test_scan_inter_only():
    report = scan(envs=[{"KEY": "v1"}, {"KEY": "v2"}])
    assert report.has_duplicates
    assert "KEY" in report.inter


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------

def test_format_no_duplicates_message():
    report = DuplicateReport()
    out = format_report(report, color=False)
    assert "No duplicate keys" in out


def test_format_intra_shows_key_and_count():
    report = DuplicateReport(intra={"FOO": 2})
    out = format_report(report, color=False)
    assert "FOO" in out
    assert "2x" in out


def test_format_inter_shows_key():
    report = DuplicateReport(inter=["SHARED"])
    out = format_report(report, color=False)
    assert "SHARED" in out
