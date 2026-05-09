"""Scope filtering: restrict an env dict to a named set of allowed keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    """Result of a scoping operation."""

    scope: str
    included: Dict[str, Optional[str]] = field(default_factory=dict)
    excluded: List[str] = field(default_factory=list)

    def __len__(self) -> int:  # noqa: D105
        return len(self.included)

    def has_exclusions(self) -> bool:
        """Return True when at least one key was excluded."""
        return bool(self.excluded)

    def summary(self) -> str:
        """Human-readable one-liner."""
        return (
            f"Scope '{self.scope}': {len(self.included)} included, "
            f"{len(self.excluded)} excluded."
        )


def scope_env(
    env: Dict[str, Optional[str]],
    allowed_keys: List[str],
    scope: str = "default",
) -> ScopeResult:
    """Return only the *allowed_keys* from *env*.

    Parameters
    ----------
    env:
        Parsed environment mapping (key -> value | None).
    allowed_keys:
        Ordered list of keys that belong to this scope.
    scope:
        A label for the scope (used in the result and summary).

    Returns
    -------
    ScopeResult
        Contains the filtered mapping and the list of excluded keys.
    """
    allowed_set = set(allowed_keys)
    included: Dict[str, Optional[str]] = {}
    excluded: List[str] = []

    for key, value in env.items():
        if key in allowed_set:
            included[key] = value
        else:
            excluded.append(key)

    return ScopeResult(scope=scope, included=included, excluded=excluded)
