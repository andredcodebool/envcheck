"""Tests for envcheck.renamer."""

from __future__ import annotations

import pytest

from envcheck.renamer import (
    RenameRule,
    apply_rules,
    rules_from_dict,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _rules(*pairs: tuple) -> list:
    return [RenameRule(pattern=p, replacement=r) for p, r in pairs]


# ---------------------------------------------------------------------------
# apply_rules – basic behaviour
# ---------------------------------------------------------------------------

def test_exact_rename_changes_key():
    env = {"OLD_KEY": "value"}
    result, report = apply_rules(env, _rules(("OLD_KEY", "NEW_KEY")))
    assert "NEW_KEY" in result
    assert result["NEW_KEY"] == "value"
    assert "OLD_KEY" not in result


def test_renamed_recorded_in_report():
    env = {"FOO": "1"}
    _, report = apply_rules(env, _rules(("FOO", "BAR")))
    assert report.renamed == {"FOO": "BAR"}


def test_unmatched_key_passed_through():
    env = {"KEEP": "x", "RENAME": "y"}
    result, report = apply_rules(env, _rules(("RENAME", "RENAMED")))
    assert "KEEP" in result
    assert "KEEP" in report.skipped


def test_multiple_rules_first_match_wins():
    env = {"A": "1"}
    rules = _rules(("A", "FIRST"), ("A", "SECOND"))
    result, report = apply_rules(env, rules)
    assert "FIRST" in result
    assert "SECOND" not in result


def test_values_preserved_after_rename():
    env = {"X": "hello"}
    result, _ = apply_rules(env, _rules(("X", "Y")))
    assert result["Y"] == "hello"


def test_empty_env_returns_empty():
    result, report = apply_rules({}, _rules(("A", "B")))
    assert result == {}
    assert report.renamed == {}
    assert report.skipped == []


# ---------------------------------------------------------------------------
# conflict detection
# ---------------------------------------------------------------------------

def test_conflict_recorded_when_two_keys_map_to_same_name():
    env = {"A": "1", "B": "2"}
    rules = _rules(("A", "C"), ("B", "C"))
    result, report = apply_rules(env, rules)
    assert len(report.conflicts) == 1
    # The second key keeps its original name
    assert "B" in result
    assert result["C"] == "1"  # first mapping wins


# ---------------------------------------------------------------------------
# regex rules
# ---------------------------------------------------------------------------

def test_regex_rule_renames_by_pattern():
    env = {"APP_HOST": "localhost", "APP_PORT": "5432", "OTHER": "x"}
    rules = [RenameRule(pattern=r"APP_(.*)", replacement=r"SVC_\1", regex=True)]
    result, report = apply_rules(env, rules)
    assert "SVC_HOST" in result
    assert "SVC_PORT" in result
    assert "OTHER" in result  # no match → skipped
    assert set(report.renamed.keys()) == {"APP_HOST", "APP_PORT"}


def test_regex_no_match_skips_key():
    env = {"UNRELATED": "v"}
    rules = [RenameRule(pattern=r"APP_(.*)", replacement=r"SVC_\1", regex=True)]
    _, report = apply_rules(env, rules)
    assert "UNRELATED" in report.skipped


# ---------------------------------------------------------------------------
# rules_from_dict
# ---------------------------------------------------------------------------

def test_rules_from_dict_creates_exact_rules():
    rules = rules_from_dict({"OLD": "NEW", "FOO": "BAR"})
    assert len(rules) == 2
    assert all(not r.regex for r in rules)
    patterns = {r.pattern for r in rules}
    assert patterns == {"OLD", "FOO"}


def test_rules_from_dict_regex_flag_propagated():
    rules = rules_from_dict({"APP_(.*)": r"SVC_\1"}, regex=True)
    assert rules[0].regex is True
