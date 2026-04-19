"""Transform env variable dictionaries: rename, filter, merge."""
from __future__ import annotations

from typing import Dict, List, Optional

EnvMap = Dict[str, str]


def rename_keys(env: EnvMap, mapping: Dict[str, str]) -> EnvMap:
    """Return a new env map with keys renamed according to *mapping*.

    Keys not in *mapping* are passed through unchanged.  If a source key
    does not exist in *env* it is silently skipped.
    """
    result = {}
    for k, v in env.items():
        result[mapping.get(k, k)] = v
    return result


def filter_keys(
    env: EnvMap,
    *,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> EnvMap:
    """Return a subset of *env*.

    *include* – if given, only these keys are kept.
    *exclude* – if given, these keys are dropped (applied after include).
    """
    result = dict(env)
    if include is not None:
        result = {k: v for k, v in result.items() if k in include}
    if exclude is not None:
        result = {k: v for k, v in result.items() if k not in exclude}
    return result


def merge_envs(*envs: EnvMap, strategy: str = "last") -> EnvMap:
    """Merge multiple env maps.

    strategy='last'  – later maps overwrite earlier ones (default).
    strategy='first' – earlier values win; later maps do not overwrite.
    """
    if strategy not in ("last", "first"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")
    result: EnvMap = {}
    for env in envs:
        for k, v in env.items():
            if strategy == "first" and k in result:
                continue
            result[k] = v
    return result


def prefix_keys(env: EnvMap, prefix: str) -> EnvMap:
    """Return a new env map with *prefix* prepended to every key."""
    return {f"{prefix}{k}": v for k, v in env.items()}


def strip_prefix(env: EnvMap, prefix: str) -> EnvMap:
    """Return a new env map with *prefix* removed from matching keys.

    Keys that do not start with *prefix* are passed through unchanged.
    """
    result = {}
    for k, v in env.items():
        result[k[len(prefix):] if k.startswith(prefix) else k] = v
    return result
