"""Sort and group environment variable dictionaries."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple


EnvMap = Dict[str, str]


def sort_keys(env: EnvMap, reverse: bool = False) -> EnvMap:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items(), key=lambda kv: kv[0], reverse=reverse))


def group_by_prefix(
    env: EnvMap, sep: str = "_"
) -> Dict[str, EnvMap]:
    """Group keys by their first prefix segment.

    Keys with no separator are placed under the empty-string group.
    """
    groups: Dict[str, EnvMap] = {}
    for key, value in env.items():
        prefix, _, _ = key.partition(sep)
        bucket = prefix if sep in key else ""
        groups.setdefault(bucket, {})[key] = value
    return groups


def sort_by_value_length(env: EnvMap, reverse: bool = False) -> EnvMap:
    """Return a new dict with entries sorted by value length."""
    return dict(
        sorted(env.items(), key=lambda kv: len(kv[1]), reverse=reverse)
    )


def partition_by_prefix(
    env: EnvMap, prefixes: List[str], sep: str = "_"
) -> Tuple[EnvMap, EnvMap]:
    """Split *env* into two dicts: keys whose prefix is in *prefixes* and the rest.

    Returns ``(matched, unmatched)``.
    """
    matched: EnvMap = {}
    unmatched: EnvMap = {}
    for key, value in env.items():
        prefix = key.split(sep, 1)[0] if sep in key else ""
        if prefix in prefixes:
            matched[key] = value
        else:
            unmatched[key] = value
    return matched, unmatched


def format_sorted(
    env: EnvMap,
    header: Optional[str] = None,
    sep: str = "=",
) -> str:
    """Return a sorted .env-style string representation of *env*."""
    lines: List[str] = []
    if header:
        lines.append(f"# {header}")
    for key, value in sort_keys(env).items():
        lines.append(f"{key}{sep}{value}")
    return "\n".join(lines)
