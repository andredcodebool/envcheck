"""Diff two env variable sets and report additions, removals, and changes."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DiffResult:
    added: List[str] = field(default_factory=list)    # keys in new, not in old
    removed: List[str] = field(default_factory=list)  # keys in old, not in new
    changed: List[str] = field(default_factory=list)  # keys in both but different values
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_envs(
    old: Dict[str, str],
    new: Dict[str, str],
    *,
    ignore_values: bool = False,
) -> DiffResult:
    """Compare two env dicts and return a DiffResult.

    Args:
        old: baseline env mapping.
        new: updated env mapping.
        ignore_values: if True, only compare key presence, not values.
    """
    old_keys = set(old)
    new_keys = set(new)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    common = sorted(old_keys & new_keys)

    changed: List[str] = []
    unchanged: List[str] = []

    for key in common:
        if not ignore_values and old[key] != new[key]:
            changed.append(key)
        else:
            unchanged.append(key)

    return DiffResult(added=added, removed=removed, changed=changed, unchanged=unchanged)


def format_diff(result: DiffResult, *, color: bool = True) -> str:
    """Return a human-readable diff summary string."""
    GREEN = "\033[32m" if color else ""
    RED = "\033[31m" if color else ""
    YELLOW = "\033[33m" if color else ""
    RESET = "\033[0m" if color else ""

    lines: List[str] = []
    for key in result.added:
        lines.append(f"{GREEN}+ {key}{RESET}")
    for key in result.removed:
        lines.append(f"{RED}- {key}{RESET}")
    for key in result.changed:
        lines.append(f"{YELLOW}~ {key}{RESET}")

    if not lines:
        return "No differences found."
    return "\n".join(lines)
