"""trimmer.py – Remove keys from an env mapping by name or pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TrimResult:
    """Result returned by :func:`trim_env`."""

    original: Dict[str, Optional[str]]
    trimmed: Dict[str, Optional[str]]
    removed_keys: List[str] = field(default_factory=list)

    def __len__(self) -> int:  # number of removed keys
        return len(self.removed_keys)

    def has_removals(self) -> bool:
        """Return True when at least one key was removed."""
        return bool(self.removed_keys)

    def summary(self) -> str:
        if not self.removed_keys:
            return "No keys removed."
        keys = ", ".join(self.removed_keys)
        return f"Removed {len(self.removed_keys)} key(s): {keys}"


def trim_env(
    env: Dict[str, Optional[str]],
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
) -> TrimResult:
    """Return a copy of *env* with matching keys removed.

    Parameters
    ----------
    env:
        Source mapping produced by :func:`~envsync.parser.parse_env_file`.
    keys:
        Explicit list of key names to remove (exact match, case-sensitive).
    pattern:
        Regular-expression pattern; any key whose name matches is removed.

    At least one of *keys* or *pattern* must be supplied.
    """
    if not keys and pattern is None:
        raise ValueError("Provide at least one of 'keys' or 'pattern'.")

    exact: set[str] = set(keys or [])
    compiled = re.compile(pattern) if pattern else None

    removed: List[str] = []
    result: Dict[str, Optional[str]] = {}

    for key, value in env.items():
        drop = key in exact or (compiled is not None and compiled.search(key))
        if drop:
            removed.append(key)
        else:
            result[key] = value

    return TrimResult(original=dict(env), trimmed=result, removed_keys=removed)
