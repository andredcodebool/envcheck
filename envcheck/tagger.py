"""Tag environment variables with arbitrary labels and filter/query by tag."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set


@dataclass
class TagReport:
    tagged: Dict[str, Set[str]] = field(default_factory=dict)   # key -> tags
    untagged: List[str] = field(default_factory=list)


def tag_env(
    env: Dict[str, str],
    tag_map: Dict[str, List[str]],
) -> TagReport:
    """Associate tags with env keys based on *tag_map* (key -> list[tag]).

    Keys present in *env* but absent from *tag_map* are recorded as untagged.
    Keys in *tag_map* that are not in *env* are silently ignored.
    """
    tagged: Dict[str, Set[str]] = {}
    for key in env:
        if key in tag_map:
            tagged[key] = set(tag_map[key])
    untagged = [k for k in env if k not in tag_map]
    return TagReport(tagged=tagged, untagged=sorted(untagged))


def filter_by_tag(report: TagReport, tag: str) -> List[str]:
    """Return sorted list of keys that carry *tag*."""
    return sorted(k for k, tags in report.tagged.items() if tag in tags)


def all_tags(report: TagReport) -> Set[str]:
    """Return the union of all tags present in *report*."""
    result: Set[str] = set()
    for tags in report.tagged.values():
        result |= tags
    return result


def tags_from_dict(raw: Dict[str, object]) -> Dict[str, List[str]]:
    """Parse a plain dict such as one loaded from TOML/JSON config.

    Expected shape::

        {"DB_URL": ["database", "secret"], "PORT": ["network"]}

    String values are wrapped in a list for convenience.
    """
    result: Dict[str, List[str]] = {}
    for key, value in raw.items():
        if isinstance(value, str):
            result[key] = [value]
        elif isinstance(value, Iterable):
            result[key] = list(value)
        else:
            raise TypeError(f"Tag value for {key!r} must be a string or list, got {type(value).__name__}")
    return result


def format_tag_report(report: TagReport) -> str:
    """Return a human-readable summary of the tag report."""
    lines: List[str] = []
    if report.tagged:
        lines.append("Tagged keys:")
        for key in sorted(report.tagged):
            tags_str = ", ".join(sorted(report.tagged[key]))
            lines.append(f"  {key}: [{tags_str}]")
    if report.untagged:
        lines.append("Untagged keys:")
        for key in report.untagged:
            lines.append(f"  {key}")
    if not lines:
        lines.append("No keys found.")
    return "\n".join(lines)
