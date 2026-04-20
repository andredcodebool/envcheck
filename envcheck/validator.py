"""Value-level validation rules for environment variables."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class ValidationIssue:
    key: str
    value: str
    rule: str
    message: str


@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0


# Built-in rule implementations

def _rule_nonempty(key: str, value: str) -> Optional[ValidationIssue]:
    if not value.strip():
        return ValidationIssue(key, value, "nonempty", "value must not be empty")
    return None


def _rule_url(key: str, value: str) -> Optional[ValidationIssue]:
    pattern = re.compile(r'^https?://.+', re.IGNORECASE)
    if not pattern.match(value):
        return ValidationIssue(key, value, "url", "value must be a valid http/https URL")
    return None


def _rule_integer(key: str, value: str) -> Optional[ValidationIssue]:
    try:
        int(value)
    except ValueError:
        return ValidationIssue(key, value, "integer", "value must be an integer")
    return None


def _rule_boolean(key: str, value: str) -> Optional[ValidationIssue]:
    if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
        return ValidationIssue(key, value, "boolean", "value must be a boolean (true/false/1/0/yes/no)")
    return None


RULE_REGISTRY: Dict[str, Callable[[str, str], Optional[ValidationIssue]]] = {
    "nonempty": _rule_nonempty,
    "url": _rule_url,
    "integer": _rule_integer,
    "boolean": _rule_boolean,
}


def validate(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    extra_rules: Optional[Dict[str, Callable[[str, str], Optional[ValidationIssue]]]] = None,
) -> ValidationReport:
    """Validate *env* values against *rules* mapping key -> list[rule_name]."""
    registry = {**RULE_REGISTRY, **(extra_rules or {})}
    issues: List[ValidationIssue] = []
    for key, rule_names in rules.items():
        if key not in env:
            continue
        value = env[key]
        for rule_name in rule_names:
            fn = registry.get(rule_name)
            if fn is None:
                continue
            issue = fn(key, value)
            if issue:
                issues.append(issue)
    return ValidationReport(issues=issues)


def format_validation(report: ValidationReport) -> str:
    """Return a human-readable summary of a ValidationReport."""
    if report.ok:
        return "validation passed — no issues found"
    lines = [f"validation failed — {len(report.issues)} issue(s):",]
    for issue in report.issues:
        lines.append(f"  [{issue.rule}] {issue.key}={issue.value!r}: {issue.message}")
    return "\n".join(lines)
