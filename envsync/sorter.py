"""Sort and group .env file keys by prefix or alphabetically."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    """Result of a sort operation on an env mapping."""

    sorted_env: Dict[str, Optional[str]]
    groups: Dict[str, Dict[str, Optional[str]]]
    ungrouped: Dict[str, Optional[str]]

    def __len__(self) -> int:  # noqa: D105
        return len(self.sorted_env)

    def summary(self) -> str:  # noqa: D102
        group_names = ", ".join(self.groups.keys()) if self.groups else "none"
        return (
            f"{len(self.sorted_env)} keys sorted; "
            f"groups: {group_names}; "
            f"ungrouped: {len(self.ungrouped)}"
        )


def _prefix(key: str) -> Optional[str]:
    """Return the prefix (part before the first '_') if one exists."""
    if "_" in key:
        return key.split("_", 1)[0]
    return None


def sort_env(
    env: Dict[str, Optional[str]],
    *,
    group_by_prefix: bool = False,
    reverse: bool = False,
) -> SortResult:
    """Sort *env* keys alphabetically, optionally grouping by prefix.

    Parameters
    ----------
    env:
        Mapping of key -> value to sort.
    group_by_prefix:
        When *True*, keys that share a common prefix (the segment before the
        first underscore) are collected into named groups.
    reverse:
        When *True*, sort in descending order.
    """
    sorted_keys: List[str] = sorted(env.keys(), reverse=reverse)
    sorted_env: Dict[str, Optional[str]] = {k: env[k] for k in sorted_keys}

    groups: Dict[str, Dict[str, Optional[str]]] = {}
    ungrouped: Dict[str, Optional[str]] = {}

    if group_by_prefix:
        for key in sorted_keys:
            pfx = _prefix(key)
            if pfx:
                groups.setdefault(pfx, {})[key] = env[key]
            else:
                ungrouped[key] = env[key]
    else:
        ungrouped = dict(sorted_env)

    return SortResult(
        sorted_env=sorted_env,
        groups=groups,
        ungrouped=ungrouped,
    )
