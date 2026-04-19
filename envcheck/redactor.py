"""Utilities for redacting sensitive environment variable values."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Optional

# Patterns whose matched key names are considered sensitive by default
_SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)(password|passwd|secret|token|api_key|apikey|private_key|auth)"),
]

REDACTED = "***REDACTED***"


def is_sensitive(key: str, extra_patterns: Optional[Iterable[str]] = None) -> bool:
    """Return True if *key* looks like it holds a sensitive value."""
    patterns = list(_SENSITIVE_PATTERNS)
    if extra_patterns:
        patterns += [re.compile(p) for p in extra_patterns]
    return any(p.search(key) for p in patterns)


def redact(
    env: Dict[str, str],
    extra_patterns: Optional[Iterable[str]] = None,
    redact_value: str = REDACTED,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by *redact_value*."""
    return {
        k: (redact_value if is_sensitive(k, extra_patterns) else v)
        for k, v in env.items()
    }


def redact_string(
    raw: str,
    extra_patterns: Optional[Iterable[str]] = None,
    redact_value: str = REDACTED,
) -> str:
    """Return *raw* (KEY=VALUE lines) with sensitive values replaced."""
    lines: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            lines.append(line)
            continue
        key, _, value = stripped.partition("=")
        if is_sensitive(key.strip(), extra_patterns):
            lines.append(f"{key.strip()}={redact_value}")
        else:
            lines.append(line)
    return "\n".join(lines)
