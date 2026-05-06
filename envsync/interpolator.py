"""Variable interpolation for .env files.

Supports ${VAR} and $VAR syntax for referencing other variables
defined in the same env mapping.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

_BRACE_RE = re.compile(r"\$\{([^}]+)\}")
_BARE_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


class InterpolationError(ValueError):
    """Raised when a referenced variable cannot be resolved."""


def _resolve_value(
    value: str,
    env: Dict[str, Optional[str]],
    key: str,
    strict: bool,
) -> str:
    """Replace all variable references in *value* using *env*."""

    def replace(match: re.Match) -> str:  # type: ignore[type-arg]
        ref = match.group(1)
        if ref == key:
            raise InterpolationError(
                f"Self-referencing variable: '{key}'"
            )
        if ref not in env:
            if strict:
                raise InterpolationError(
                    f"Variable '{key}' references undefined variable '{ref}'"
                )
            return match.group(0)  # leave unresolved
        resolved = env[ref]
        return "" if resolved is None else resolved

    # Expand ${VAR} first, then bare $VAR
    value = _BRACE_RE.sub(replace, value)
    value = _BARE_RE.sub(replace, value)
    return value


def interpolate(
    env: Dict[str, Optional[str]],
    strict: bool = False,
) -> Dict[str, Optional[str]]:
    """Return a new mapping with variable references expanded.

    Parameters
    ----------
    env:
        Parsed env mapping (key -> value | None).
    strict:
        When *True*, raise :class:`InterpolationError` for any
        reference to an undefined variable.  When *False* (default)
        unresolvable references are left as-is.
    """
    result: Dict[str, Optional[str]] = {}
    for key, value in env.items():
        if value is None:
            result[key] = None
        else:
            result[key] = _resolve_value(value, env, key, strict)
    return result
