"""Tests for envcheck.sorter."""
import pytest

from envcheck.sorter import (
    format_sorted,
    group_by_prefix,
    partition_by_prefix,
    sort_by_value_length,
    sort_keys,
)


SAMPLE: dict[str, str] = {
    "ZEBRA": "last",
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_URL": "postgres://localhost/db",
    "ALPHA": "first",
}


def test_sort_keys_ascending():
    result = sort_keys(SAMPLE)
    assert list(result.keys()) == sorted(SAMPLE.keys())


def test_sort_keys_descending():
    result = sort_keys(SAMPLE, reverse=True)
    assert list(result.keys()) == sorted(SAMPLE.keys(), reverse=True)


def test_sort_keys_preserves_values():
    result = sort_keys(SAMPLE)
    for k, v in SAMPLE.items():
        assert result[k] == v


def test_group_by_prefix_groups_correctly():
    groups = group_by_prefix(SAMPLE)
    assert "APP" in groups
    assert "DB" in groups
    assert set(groups["APP"].keys()) == {"APP_HOST", "APP_PORT"}
    assert set(groups["DB"].keys()) == {"DB_URL"}


def test_group_by_prefix_no_sep_goes_to_empty_bucket():
    groups = group_by_prefix(SAMPLE)
    assert "" in groups
    assert "ZEBRA" in groups[""]
    assert "ALPHA" in groups[""]


def test_group_by_prefix_custom_sep():
    env = {"APP.HOST": "h", "APP.PORT": "p", "PLAIN": "v"}
    groups = group_by_prefix(env, sep=".")
    assert set(groups["APP"].keys()) == {"APP.HOST", "APP.PORT"}
    assert "PLAIN" in groups[""]


def test_sort_by_value_length_ascending():
    env = {"A": "hi", "B": "hello world", "C": "hey"}
    result = sort_by_value_length(env)
    lengths = [len(v) for v in result.values()]
    assert lengths == sorted(lengths)


def test_sort_by_value_length_descending():
    env = {"A": "hi", "B": "hello world", "C": "hey"}
    result = sort_by_value_length(env, reverse=True)
    lengths = [len(v) for v in result.values()]
    assert lengths == sorted(lengths, reverse=True)


def test_partition_by_prefix_matched_and_unmatched():
    matched, unmatched = partition_by_prefix(SAMPLE, ["APP", "DB"])
    assert set(matched.keys()) == {"APP_HOST", "APP_PORT", "DB_URL"}
    assert set(unmatched.keys()) == {"ZEBRA", "ALPHA"}


def test_partition_by_prefix_empty_prefixes():
    matched, unmatched = partition_by_prefix(SAMPLE, [])
    assert matched == {}
    assert unmatched == SAMPLE


def test_format_sorted_output_is_sorted():
    output = format_sorted(SAMPLE)
    lines = output.splitlines()
    keys = [line.split("=")[0] for line in lines]
    assert keys == sorted(keys)


def test_format_sorted_includes_header():
    output = format_sorted({"Z": "1", "A": "2"}, header="My Config")
    assert output.startswith("# My Config")


def test_format_sorted_no_header():
    output = format_sorted({"KEY": "val"})
    assert not output.startswith("#")
