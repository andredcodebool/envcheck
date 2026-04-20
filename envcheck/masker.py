"""masker.py — mask env var values for safe display in logs and reports."""

from __future__ import annotations

from typing import Dict, Optional

from envcheck.redactor import is_sensitive

_DEFAULT_MASK = "********"
_VISIBLE_CHARS = 4


def mask_value(
    key: str,
    value: str,
    *,
    mask: str = _DEFAULT_MASK,
    show_prefix: bool = False,
    extra_patterns: Optional[list[str]] = None,
) -> str:
    """Return *value* masked if *key* looks sensitive.

    Parameters
    ----------
    key:             The environment variable name.
    value:           The raw value to potentially mask.
    mask:            Replacement string used when masking (default: ``********``).
    show_prefix:     When True, show the first ``_VISIBLE_CHARS`` characters
                     followed by the mask, e.g. ``abcd****``.
    extra_patterns:  Additional regex patterns forwarded to :func:`is_sensitive`.
    """
    kwargs: dict = {}
    if extra_patterns is not None:
        kwargs["extra_patterns"] = extra_patterns

    if not is_sensitive(key, **kwargs):
        return value

    if show_prefix and len(value) > _VISIBLE_CHARS:
        return value[:_VISIBLE_CHARS] + mask

    return mask


def mask_env(
    env: Dict[str, str],
    *,
    mask: str = _DEFAULT_MASK,
    show_prefix: bool = False,
    extra_patterns: Optional[list[str]] = None,
) -> Dict[str, str]:
    """Return a new dict with all sensitive values masked."""
    return {
        k: mask_value(
            k,
            v,
            mask=mask,
            show_prefix=show_prefix,
            extra_patterns=extra_patterns,
        )
        for k, v in env.items()
    }


def mask_string(
    line: str,
    *,
    mask: str = _DEFAULT_MASK,
    show_prefix: bool = False,
    extra_patterns: Optional[list[str]] = None,
) -> str:
    """Mask the value portion of a ``KEY=VALUE`` line if the key is sensitive.

    Lines that do not follow ``KEY=VALUE`` syntax are returned unchanged.
    """
    if "=" not in line:
        return line
    key, _, value = line.partition("=")
    masked = mask_value(
        key.strip(),
        value,
        mask=mask,
        show_prefix=show_prefix,
        extra_patterns=extra_patterns,
    )
    return f"{key}={masked}"
