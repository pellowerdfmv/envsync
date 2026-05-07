"""Group .env keys by prefix or custom delimiter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    """Result of grouping an env mapping by key prefix."""

    groups: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)
    ungrouped: Dict[str, Optional[str]] = field(default_factory=dict)

    def __len__(self) -> int:  # number of distinct groups (excluding ungrouped)
        return len(self.groups)

    def group_names(self) -> List[str]:
        """Sorted list of group names."""
        return sorted(self.groups.keys())

    def summary(self) -> str:
        parts = [f"{name!r}: {len(keys)} key(s)" for name, keys in sorted(self.groups.items())]
        if self.ungrouped:
            parts.append(f"(ungrouped): {len(self.ungrouped)} key(s)")
        return ", ".join(parts) if parts else "no keys"


def _prefix(key: str, delimiter: str) -> Optional[str]:
    """Return the portion of *key* before the first occurrence of *delimiter*.

    Returns ``None`` when the delimiter is absent or the prefix would be empty.
    """
    if delimiter not in key:
        return None
    prefix = key.split(delimiter, 1)[0]
    return prefix if prefix else None


def group_env(
    env: Dict[str, Optional[str]],
    delimiter: str = "_",
) -> GroupResult:
    """Group *env* keys by the leading segment separated by *delimiter*.

    Keys that have no delimiter (or whose prefix is empty) land in
    ``GroupResult.ungrouped``.

    Parameters
    ----------
    env:
        Mapping of key → value (values may be ``None``).
    delimiter:
        Character (or string) used to split keys into prefix + remainder.
        Defaults to ``"_"``.
    """
    groups: Dict[str, Dict[str, Optional[str]]] = {}
    ungrouped: Dict[str, Optional[str]] = {}

    for key, value in env.items():
        p = _prefix(key, delimiter)
        if p is None:
            ungrouped[key] = value
        else:
            groups.setdefault(p, {})[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped)
