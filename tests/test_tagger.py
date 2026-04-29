"""Tests for envcheck.tagger."""
import pytest
from envcheck.tagger import (
    TagReport,
    all_tags,
    filter_by_tag,
    format_tag_report,
    tag_env,
    tags_from_dict,
)


ENV = {"DB_URL": "postgres://", "PORT": "5432", "SECRET_KEY": "abc", "DEBUG": "true"}
TAG_MAP = {
    "DB_URL": ["database", "secret"],
    "SECRET_KEY": ["secret"],
    "PORT": ["network"],
}


def test_tag_env_tagged_keys():
    report = tag_env(ENV, TAG_MAP)
    assert set(report.tagged.keys()) == {"DB_URL", "SECRET_KEY", "PORT"}


def test_tag_env_untagged_keys():
    report = tag_env(ENV, TAG_MAP)
    assert report.untagged == ["DEBUG"]


def test_tag_env_correct_tags_assigned():
    report = tag_env(ENV, TAG_MAP)
    assert report.tagged["DB_URL"] == {"database", "secret"}
    assert report.tagged["PORT"] == {"network"}


def test_tag_env_key_not_in_env_ignored():
    tag_map = {"MISSING_KEY": ["ghost"], "PORT": ["network"]}
    report = tag_env(ENV, tag_map)
    assert "MISSING_KEY" not in report.tagged


def test_filter_by_tag_returns_matching_keys():
    report = tag_env(ENV, TAG_MAP)
    assert filter_by_tag(report, "secret") == ["DB_URL", "SECRET_KEY"]


def test_filter_by_tag_no_match_returns_empty():
    report = tag_env(ENV, TAG_MAP)
    assert filter_by_tag(report, "nonexistent") == []


def test_all_tags_union():
    report = tag_env(ENV, TAG_MAP)
    assert all_tags(report) == {"database", "secret", "network"}


def test_all_tags_empty_report():
    assert all_tags(TagReport()) == set()


def test_tags_from_dict_list_values():
    raw = {"DB_URL": ["database", "secret"], "PORT": ["network"]}
    result = tags_from_dict(raw)
    assert result["DB_URL"] == ["database", "secret"]


def test_tags_from_dict_string_value_wrapped():
    raw = {"PORT": "network"}
    result = tags_from_dict(raw)
    assert result["PORT"] == ["network"]


def test_tags_from_dict_invalid_type_raises():
    with pytest.raises(TypeError, match="must be a string or list"):
        tags_from_dict({"PORT": 123})


def test_format_tag_report_contains_tagged_section():
    report = tag_env(ENV, TAG_MAP)
    output = format_tag_report(report)
    assert "Tagged keys:" in output
    assert "DB_URL" in output


def test_format_tag_report_contains_untagged_section():
    report = tag_env(ENV, TAG_MAP)
    output = format_tag_report(report)
    assert "Untagged keys:" in output
    assert "DEBUG" in output


def test_format_tag_report_empty():
    output = format_tag_report(TagReport())
    assert "No keys found" in output
