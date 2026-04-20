"""Bulk key renaming via pattern rules for env mappings."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class RenameRule:
    """A single rename rule: match a key pattern and replace with a target."""

    pattern: str
    replacement: str
    regex: bool = False


@dataclass
class RenameReport:
    renamed: Dict[str, str] = field(default_factory=dict)   # old -> new
    skipped: List[str] = field(default_factory=list)         # keys with no match
    conflicts: List[str] = field(default_factory=list)       # new names that collide


def _apply_rule(key: str, rule: RenameRule) -> Optional[str]:
    """Return the new key name if the rule matches, else None."""
    if rule.regex:
        m = re.fullmatch(rule.pattern, key)
        if m:
            return re.sub(rule.pattern, rule.replacement, key)
        return None
    if key == rule.pattern:
        return rule.replacement
    return None


def apply_rules(
    env: Dict[str, str],
    rules: List[RenameRule],
) -> Tuple[Dict[str, str], RenameReport]:
    """Apply rename rules to *env* and return the updated mapping plus a report.

    Rules are applied in order; the first matching rule wins for each key.
    Keys with no matching rule are passed through unchanged and recorded as
    *skipped* in the report.  Collisions (two old keys mapping to the same new
    name) are recorded in *conflicts* and the second key is left under its
    original name.
    """
    report = RenameReport()
    result: Dict[str, str] = {}
    seen_new: Dict[str, str] = {}  # new_name -> original old key

    for key, value in env.items():
        new_key: Optional[str] = None
        for rule in rules:
            candidate = _apply_rule(key, rule)
            if candidate is not None:
                new_key = candidate
                break

        if new_key is None:
            report.skipped.append(key)
            result[key] = value
            continue

        if new_key in seen_new:
            report.conflicts.append(key)
            result[key] = value  # keep original name on conflict
        else:
            seen_new[new_key] = key
            report.renamed[key] = new_key
            result[new_key] = value

    return result, report


def rules_from_dict(mapping: Dict[str, str], regex: bool = False) -> List[RenameRule]:
    """Build a list of :class:`RenameRule` from a plain ``{old: new}`` dict."""
    return [RenameRule(pattern=k, replacement=v, regex=regex) for k, v in mapping.items()]
