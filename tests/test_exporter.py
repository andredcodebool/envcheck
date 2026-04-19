"""Tests for envcheck.exporter."""
import csv
import io
import json

import pytest

from envcheck.checker import CheckResult
from envcheck.exporter import export_csv, export_json, result_to_dict


def _make(ok=True, missing=None, extra=None, total_required=3, total_present=3):
    return CheckResult(
        ok=ok,
        missing=missing or [],
        extra=extra or [],
        total_required=total_required,
        total_present=total_present,
    )


def test_result_to_dict_ok():
    r = _make(ok=True)
    d = result_to_dict(r)
    assert d["ok"] is True
    assert d["missing"] == []
    assert d["extra"] == []


def test_result_to_dict_missing_sorted():
    r = _make(ok=False, missing=["Z_KEY", "A_KEY"])
    d = result_to_dict(r)
    assert d["missing"] == ["A_KEY", "Z_KEY"]


def test_export_json_structure():
    results = [_make(ok=True), _make(ok=False, missing=["FOO"])]
    labels = ["svc-a", "svc-b"]
    out = export_json(results, labels)
    data = json.loads(out)
    assert len(data) == 2
    assert data[0]["label"] == "svc-a"
    assert data[0]["ok"] is True
    assert data[1]["label"] == "svc-b"
    assert "FOO" in data[1]["missing"]


def test_export_json_auto_labels():
    results = [_make()]
    out = export_json(results)
    data = json.loads(out)
    assert data[0]["label"] == "env_0"


def test_export_csv_header():
    out = export_csv([_make()], ["svc"])
    reader = csv.DictReader(io.StringIO(out))
    assert set(reader.fieldnames) >= {"label", "ok", "missing", "extra"}


def test_export_csv_row_values():
    r = _make(ok=False, missing=["BAR", "BAZ"], extra=["EXTRA"])
    out = export_csv([r], ["my-svc"])
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 1
    row = rows[0]
    assert row["label"] == "my-svc"
    assert row["ok"] == "False"
    missing_keys = row["missing"].split(";")
    assert "BAR" in missing_keys
    assert "BAZ" in missing_keys
    assert row["extra"] == "EXTRA"


def test_export_csv_multiple_rows():
    results = [_make(ok=True), _make(ok=False, missing=["X"])]
    out = export_csv(results)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 2
