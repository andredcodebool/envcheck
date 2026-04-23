"""Tests for envcheck.patcher."""
import pytest
from envcheck.patcher import apply_patch, format_patch, PatchReport


BASE = {"A": "1", "B": "2", "C": "3"}


def test_add_new_key():
    result, report = apply_patch(BASE, set_keys={"D": "4"})
    assert result["D"] == "4"
    assert "D" in report.added


def test_update_existing_key():
    result, report = apply_patch(BASE, set_keys={"A": "99"})
    assert result["A"] == "99"
    assert "A" in report.updated


def test_unchanged_key_same_value():
    result, report = apply_patch(BASE, set_keys={"B": "2"})
    assert result["B"] == "2"
    assert "B" in report.unchanged
    assert "B" not in report.updated


def test_remove_existing_key():
    result, report = apply_patch(BASE, remove_keys=["C"])
    assert "C" not in result
    assert "C" in report.removed


def test_remove_missing_key_is_noop():
    result, report = apply_patch(BASE, remove_keys=["Z"])
    assert set(result.keys()) == set(BASE.keys())
    assert "Z" not in report.removed


def test_does_not_mutate_input():
    original = dict(BASE)
    apply_patch(BASE, set_keys={"X": "10"}, remove_keys=["A"])
    assert BASE == original


def test_combined_patch():
    result, report = apply_patch(
        BASE,
        set_keys={"A": "new", "NEW": "val"},
        remove_keys=["B"],
    )
    assert result["A"] == "new"
    assert result["NEW"] == "val"
    assert "B" not in result
    assert "A" in report.updated
    assert "NEW" in report.added
    assert "B" in report.removed


def test_format_patch_contains_symbols():
    _, report = apply_patch(BASE, set_keys={"NEW": "v", "A": "x"}, remove_keys=["C"])
    text = format_patch(report)
    assert "+" in text
    assert "~" in text
    assert "-" in text


def test_format_patch_summary_line():
    _, report = apply_patch(BASE, set_keys={"A": "x", "D": "d"}, remove_keys=["B"])
    text = format_patch(report)
    assert "change(s)" in text
