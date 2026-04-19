"""Tests for envcheck.audit."""
import json
from pathlib import Path

import pytest

from envcheck.audit import (
    AuditEntry,
    entry_from_check,
    list_entries,
    record,
)
from envcheck.checker import check_env


@pytest.fixture()
def audit_dir(tmp_path):
    return tmp_path / "audit"


def _entry(**kwargs) -> AuditEntry:
    defaults = dict(
        timestamp="20240101T000000Z",
        profile="default",
        source=".env",
        passed=True,
        missing=[],
        extra=[],
    )
    defaults.update(kwargs)
    return AuditEntry(**defaults)


def test_record_creates_file(audit_dir):
    e = _entry()
    path = record(e, audit_dir=audit_dir)
    assert path.exists()


def test_record_content_roundtrip(audit_dir):
    e = _entry(profile="staging", missing=["SECRET_KEY"])
    path = record(e, audit_dir=audit_dir)
    data = json.loads(path.read_text())
    assert data["profile"] == "staging"
    assert data["missing"] == ["SECRET_KEY"]


def test_list_entries_empty(audit_dir):
    assert list_entries(audit_dir=audit_dir) == []


def test_list_entries_ordered(audit_dir):
    e1 = _entry(timestamp="20240101T000000Z", profile="a")
    e2 = _entry(timestamp="20240102T000000Z", profile="b")
    record(e2, audit_dir=audit_dir)
    record(e1, audit_dir=audit_dir)
    entries = list_entries(audit_dir=audit_dir)
    assert entries[0].profile == "a"
    assert entries[1].profile == "b"


def test_list_entries_count(audit_dir):
    for i in range(3):
        record(_entry(timestamp=f"2024010{i+1}T000000Z", profile=str(i)), audit_dir=audit_dir)
    assert len(list_entries(audit_dir=audit_dir)) == 3


def test_entry_from_check_passed():
    result = check_env({"A": "1", "B": "2"}, required=["A", "B"])
    e = entry_from_check("prod", ".env", result)
    assert e.passed is True
    assert e.missing == []
    assert e.profile == "prod"


def test_entry_from_check_failed():
    result = check_env({"A": "1"}, required=["A", "B", "C"])
    e = entry_from_check("prod", ".env", result)
    assert e.passed is False
    assert set(e.missing) == {"B", "C"}
