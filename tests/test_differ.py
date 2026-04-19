"""Tests for envcheck.differ module."""

import pytest
from envcheck.differ import diff_envs, format_diff, DiffResult


OLD = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
NEW = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


def test_added_keys():
    result = diff_envs(OLD, NEW)
    assert result.added == ["SECRET"]


def test_removed_keys():
    result = diff_envs(OLD, NEW)
    assert result.removed == ["DEBUG"]


def test_changed_keys():
    result = diff_envs(OLD, NEW)
    assert result.changed == ["HOST"]


def test_unchanged_keys():
    result = diff_envs(OLD, NEW)
    assert result.unchanged == ["PORT"]


def test_has_diff_true():
    result = diff_envs(OLD, NEW)
    assert result.has_diff is True


def test_has_diff_false():
    result = diff_envs(OLD, OLD)
    assert result.has_diff is False


def test_identical_envs_all_unchanged():
    result = diff_envs(OLD, OLD)
    assert result.added == []
    assert result.removed == []
    assert result.changed == []
    assert sorted(result.unchanged) == sorted(OLD.keys())


def test_ignore_values_treats_changed_as_unchanged():
    result = diff_envs(OLD, NEW, ignore_values=True)
    assert "HOST" not in result.changed
    assert "HOST" in result.unchanged


def test_format_diff_no_color_shows_symbols():
    result = diff_envs(OLD, NEW)
    output = format_diff(result, color=False)
    assert "+ SECRET" in output
    assert "- DEBUG" in output
    assert "~ HOST" in output


def test_format_diff_no_differences():
    result = diff_envs(OLD, OLD)
    output = format_diff(result, color=False)
    assert output == "No differences found."


def test_empty_old():
    result = diff_envs({}, NEW)
    assert set(result.added) == set(NEW.keys())
    assert result.removed == []
    assert result.changed == []


def test_empty_new():
    result = diff_envs(OLD, {})
    assert set(result.removed) == set(OLD.keys())
    assert result.added == []
