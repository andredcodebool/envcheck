"""Core logic for comparing env files against an example/template."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class CheckResult:
    missing_keys: List[str] = field(default_factory=list)
    extra_keys: List[str] = field(default_factory=list)
    empty_required: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing_keys or self.empty_required)

    def summary(self) -> str:
        lines: List[str] = []
        if self.missing_keys:
            lines.append("Missing keys (required by template):")
            for k in sorted(self.missing_keys):
                lines.append(f"  - {k}")
        if self.empty_required:
            lines.append("Keys present but empty (template has a value):")
            for k in sorted(self.empty_required):
                lines.append(f"  - {k}")
        if self.extra_keys:
            lines.append("Extra keys (not in template):")
            for k in sorted(self.extra_keys):
                lines.append(f"  + {k}")
        if not lines:
            lines.append("All checks passed.")
        return "\n".join(lines)


def check_env(
    actual: Dict[str, Optional[str]],
    template: Dict[str, Optional[str]],
    *,
    strict: bool = False,
) -> CheckResult:
    """Compare *actual* env vars against a *template*.

    Args:
        actual: Parsed env variables from the real .env file.
        template: Parsed env variables from .env.example / template.
        strict: If True, extra keys in *actual* are treated as errors
                (they are still reported but don't affect ``ok`` unless
                you check ``extra_keys`` yourself).
    """
    result = CheckResult()

    template_keys: Set[str] = set(template.keys())
    actual_keys: Set[str] = set(actual.keys())

    result.missing_keys = sorted(template_keys - actual_keys)
    result.extra_keys = sorted(actual_keys - template_keys)

    for key in template_keys & actual_keys:
        template_has_value = template[key] is not None
        actual_is_empty = actual[key] is None
        if template_has_value and actual_is_empty:
            result.empty_required.append(key)

    return result
