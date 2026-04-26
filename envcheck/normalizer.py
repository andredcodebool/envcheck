"""Normalize environment variable keys and values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeReport:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)


def _normalize_key(key: str) -> str:
    """Return key uppercased with runs of whitespace replaced by underscores."""
    return key.strip().upper().replace(" ", "_").replace("-", "_")


def _normalize_value(value: str) -> str:
    """Strip leading/trailing whitespace from a value."""
    return value.strip()


def normalize_keys(env: Dict[str, str]) -> NormalizeReport:
    """Normalize all keys to UPPER_SNAKE_CASE."""
    original = dict(env)
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        new_key = _normalize_key(key)
        normalized[new_key] = value
        if new_key != key:
            changes.append(("key", key, new_key))

    return NormalizeReport(original=original, normalized=normalized, changes=changes)


def normalize_values(env: Dict[str, str]) -> NormalizeReport:
    """Strip whitespace from all values."""
    original = dict(env)
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        new_value = _normalize_value(value)
        normalized[key] = new_value
        if new_value != value:
            changes.append(("value", key, new_value))

    return NormalizeReport(original=original, normalized=normalized, changes=changes)


def normalize(env: Dict[str, str]) -> NormalizeReport:
    """Normalize both keys and values; return a combined report."""
    key_report = normalize_keys(env)
    val_report = normalize_values(key_report.normalized)

    all_changes = key_report.changes + val_report.changes
    return NormalizeReport(
        original=env,
        normalized=val_report.normalized,
        changes=all_changes,
    )


def format_normalize(report: NormalizeReport) -> str:
    """Return a human-readable summary of normalization changes."""
    if not report.changes:
        return "No changes."
    lines = [f"{len(report.changes)} change(s):"]
    for kind, old, new in report.changes:
        if kind == "key":
            lines.append(f"  key   : {old!r} -> {new!r}")
        else:
            lines.append(f"  value[{old}]: stripped whitespace -> {new!r}")
    return "\n".join(lines)
