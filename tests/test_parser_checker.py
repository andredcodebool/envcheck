"""Tests for envcheck.parser and envcheck.checker."""

from __future__ import annotations

import pytest

from envcheck.parser import parse_env_string
from envcheck.checker import check_env


TEMPLATE = """
# Database
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=

# App
SECRET_KEY=changeme
DEBUG=
"""

ACTUAL_OK = """
DB_HOST=prod.db.internal
DB_PORT=5432
DB_PASSWORD=supersecret
SECRET_KEY=abc123
DEBUG=
"""

ACTUAL_MISSING = """
DB_HOST=prod.db.internal
DB_PORT=5432
"""

ACTUAL_EMPTY_REQUIRED = """
DB_HOST=prod.db.internal
DB_PORT=5432
DB_PASSWORD=supersecret
SECRET_KEY=
DEBUG=
"""


def test_parse_env_string_basic():
    result = parse_env_string(TEMPLATE)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_PASSWORD"] is None
    assert result["SECRET_KEY"] == "changeme"
    assert result["DEBUG"] is None


def test_parse_ignores_comments_and_blanks():
    result = parse_env_string(TEMPLATE)
    assert len(result) == 5


def test_check_env_ok():
    template = parse_env_string(TEMPLATE)
    actual = parse_env_string(ACTUAL_OK)
    result = check_env(actual, template)
    assert result.ok
    assert result.missing_keys == []
    assert result.empty_required == []


def test_check_env_missing_keys():
    template = parse_env_string(TEMPLATE)
    actual = parse_env_string(ACTUAL_MISSING)
    result = check_env(actual, template)
    assert not result.ok
    assert "DB_PASSWORD" in result.missing_keys
    assert "SECRET_KEY" in result.missing_keys


def test_check_env_empty_required():
    template = parse_env_string(TEMPLATE)
    actual = parse_env_string(ACTUAL_EMPTY_REQUIRED)
    result = check_env(actual, template)
    assert not result.ok
    assert "SECRET_KEY" in result.empty_required


def test_check_env_extra_keys():
    template = parse_env_string(TEMPLATE)
    actual = parse_env_string(ACTUAL_OK + "\nEXTRA_VAR=hello\n")
    result = check_env(actual, template)
    assert "EXTRA_VAR" in result.extra_keys
    assert result.ok  # extra keys don't fail by default


def test_summary_all_passed():
    template = parse_env_string(TEMPLATE)
    actual = parse_env_string(ACTUAL_OK)
    result = check_env(actual, template)
    assert "All checks passed" in result.summary()
