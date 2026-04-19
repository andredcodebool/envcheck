"""Variable interpolation for env values (${VAR} syntax)."""
from __future__ import annotations

import re
from typing import Dict, Optional

_REF = re.compile(r"\$\{([^}]+)\}")


class InterpolationError(Exception):
    """Raised when interpolation cannot be resolved."""


def interpolate(value: str, env: Dict[str, str], *, strict: bool = False) -> str:
    """Replace ${KEY} references in *value* using *env*.

    Args:
        value:  The raw string that may contain references.
        env:    Mapping used to resolve references.
        strict: If True, raise InterpolationError for missing keys;
                otherwise leave the placeholder unchanged.
    """
    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in env:
            return env[key]
        if strict:
            raise InterpolationError(f"Undefined variable: '{key}'")
        return match.group(0)

    return _REF.sub(_replace, value)


def interpolate_all(
    env: Dict[str, str],
    *,
    strict: bool = False,
    max_passes: int = 5,
) -> Dict[str, str]:
    """Repeatedly interpolate *env* until stable or *max_passes* reached.

    Handles simple chained references (A=${B}, B=${C}) within a fixed
    iteration budget.
    """
    result = dict(env)
    for _ in range(max_passes):
        next_result = {
            k: interpolate(v, result, strict=strict) for k, v in result.items()
        }
        if next_result == result:
            break
        result = next_result
    return result


def missing_refs(value: str, env: Dict[str, str]) -> list[str]:
    """Return list of variable names referenced in *value* but absent from *env*."""
    return [m.group(1) for m in _REF.finditer(value) if m.group(1) not in env]
