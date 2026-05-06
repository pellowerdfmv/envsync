"""Redact sensitive values in a parsed env mapping before display or export."""
from __future__ import annotations

import re
from typing import Dict, FrozenSet, Optional

# Keys whose values should be redacted by default (case-insensitive substring match)
_DEFAULT_SENSITIVE_PATTERNS: tuple[str, ...] = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "auth",
    "credential",
    "cert",
    "passphrase",
)

REDACT_PLACEHOLDER = "***REDACTED***"


def _is_sensitive(key: str, patterns: tuple[str, ...]) -> bool:
    lower = key.lower()
    return any(p in lower for p in patterns)


def redact(
    env: Dict[str, Optional[str]],
    extra_patterns: Optional[tuple[str, ...]] = None,
    explicit_keys: Optional[FrozenSet[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> Dict[str, Optional[str]]:
    """Return a copy of *env* with sensitive values replaced by *placeholder*.

    Parameters
    ----------
    env:
        Parsed env mapping (key -> value | None).
    extra_patterns:
        Additional substrings to treat as sensitive (merged with defaults).
    explicit_keys:
        Exact key names that must always be redacted regardless of pattern.
    placeholder:
        The string used in place of the real value.
    """
    patterns = _DEFAULT_SENSITIVE_PATTERNS
    if extra_patterns:
        patterns = patterns + extra_patterns

    explicit_keys = explicit_keys or frozenset()
    out: Dict[str, Optional[str]] = {}

    for k, v in env.items():
        if v is None:
            out[k] = v
        elif k in explicit_keys or _is_sensitive(k, patterns):
            out[k] = placeholder
        else:
            out[k] = v

    return out


def sensitive_keys(
    env: Dict[str, Optional[str]],
    extra_patterns: Optional[tuple[str, ...]] = None,
) -> list[str]:
    """Return a sorted list of keys considered sensitive in *env*."""
    patterns = _DEFAULT_SENSITIVE_PATTERNS
    if extra_patterns:
        patterns = patterns + extra_patterns
    return sorted(k for k in env if _is_sensitive(k, patterns))
