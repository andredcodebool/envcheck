"""Tests for envcheck.interpolator."""
import pytest
from envcheck.interpolator import (
    InterpolationError,
    interpolate,
    interpolate_all,
    missing_refs,
)


def test_interpolate_simple():
    assert interpolate("hello ${NAME}", {"NAME": "world"}) == "hello world"


def test_interpolate_multiple_refs():
    env = {"A": "foo", "B": "bar"}
    assert interpolate("${A}-${B}", env) == "foo-bar"


def test_interpolate_missing_non_strict_unchanged():
    result = interpolate("${MISSING}", {})
    assert result == "${MISSING}"


def test_interpolate_missing_strict_raises():
    with pytest.raises(InterpolationError, match="MISSING"):
        interpolate("${MISSING}", {}, strict=True)


def test_interpolate_no_refs():
    assert interpolate("plain_value", {"A": "1"}) == "plain_value"


def test_interpolate_all_resolves_chain():
    env = {"A": "${B}", "B": "${C}", "C": "final"}
    result = interpolate_all(env)
    assert result["A"] == "final"
    assert result["B"] == "final"
    assert result["C"] == "final"


def test_interpolate_all_leaves_unresolvable():
    env = {"A": "${NOPE}"}
    result = interpolate_all(env)
    assert result["A"] == "${NOPE}"


def test_interpolate_all_strict_raises_on_missing():
    with pytest.raises(InterpolationError):
        interpolate_all({"A": "${GHOST}"}, strict=True)


def test_interpolate_all_returns_new_dict():
    env = {"X": "1"}
    result = interpolate_all(env)
    assert result is not env


def test_missing_refs_found():
    env = {"PRESENT": "yes"}
    refs = missing_refs("${PRESENT} ${ABSENT}", env)
    assert refs == ["ABSENT"]


def test_missing_refs_empty_when_all_present():
    env = {"A": "1", "B": "2"}
    assert missing_refs("${A}${B}", env) == []


def test_missing_refs_no_refs():
    assert missing_refs("no refs here", {}) == []
