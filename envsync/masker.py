"""Mask env values for safe display in logs or terminals."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

_SENSITIVE_SUBSTRINGS = ("password", "secret", "token", "key", "auth", "credential", "passwd", "api")

_MASK_CHAR = "*"
_VISIBLE_CHARS = 4


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(sub in lower for sub in _SENSITIVE_SUBSTRINGS)


def _mask_value(value: str, visible: int = _VISIBLE_CHARS, char: str = _MASK_CHAR) -> str:
    """Return a masked version of *value*, keeping the last *visible* chars."""
    if len(value) <= visible:
        return char * len(value)
    return char * (len(value) - visible) + value[-visible:]


@dataclass
class MaskResult:
    original: Dict[str, Optional[str]]
    masked: Dict[str, Optional[str]] = field(default_factory=dict)
    masked_keys: list = field(default_factory=list)

    def __len__(self) -> int:  # noqa: D105
        return len(self.masked_keys)

    def summary(self) -> str:
        total = len(self.original)
        count = len(self.masked_keys)
        return f"{count}/{total} keys masked"


def mask_env(
    env: Dict[str, Optional[str]],
    *,
    visible: int = _VISIBLE_CHARS,
    char: str = _MASK_CHAR,
    extra_keys: tuple[str, ...] = (),
) -> MaskResult:
    """Return a :class:`MaskResult` with sensitive values replaced by masks.

    Parameters
    ----------
    env:        Parsed env mapping (key -> value or None).
    visible:    Number of trailing characters to keep visible.
    char:       Character used for masking.
    extra_keys: Additional key names (exact, case-insensitive) to treat as sensitive.
    """
    extra_lower = {k.lower() for k in extra_keys}
    result = MaskResult(original=env)

    for key, value in env.items():
        if _is_sensitive(key) or key.lower() in extra_lower:
            result.masked_keys.append(key)
            if value is None:
                result.masked[key] = None
            else:
                result.masked[key] = _mask_value(value, visible=visible, char=char)
        else:
            result.masked[key] = value

    return result
