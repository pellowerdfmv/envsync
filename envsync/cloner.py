"""Clone an env mapping with optional key remapping and value overrides."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CloneResult:
    """Result of a clone operation."""

    cloned: Dict[str, Optional[str]]
    remapped: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    overridden: Dict[str, Optional[str]] = field(default_factory=dict)  # key -> new_val

    def __len__(self) -> int:  # noqa: D105
        return len(self.cloned)

    def has_remaps(self) -> bool:
        """Return True when at least one key was remapped."""
        return bool(self.remapped)

    def has_overrides(self) -> bool:
        """Return True when at least one value was overridden."""
        return bool(self.overridden)

    def summary(self) -> str:
        """Human-readable one-liner describing the clone."""
        parts = [f"{len(self.cloned)} key(s) cloned"]
        if self.remapped:
            parts.append(f"{len(self.remapped)} remapped")
        if self.overridden:
            parts.append(f"{len(self.overridden)} overridden")
        return ", ".join(parts) + "."


def clone_env(
    env: Dict[str, Optional[str]],
    *,
    remap: Optional[Dict[str, str]] = None,
    overrides: Optional[Dict[str, Optional[str]]] = None,
) -> CloneResult:
    """Return a deep copy of *env* with optional key renames and value patches.

    Args:
        env:       Source environment mapping.
        remap:     Mapping of ``{old_key: new_key}`` to rename during clone.
        overrides: Mapping of ``{key: value}`` applied **after** remapping.

    Returns:
        :class:`CloneResult` containing the cloned mapping and change records.
    """
    remap = remap or {}
    overrides = overrides or {}

    cloned: Dict[str, Optional[str]] = {}
    remapped: Dict[str, str] = {}

    for key, value in env.items():
        new_key = remap.get(key, key)
        if new_key != key:
            remapped[key] = new_key
        cloned[new_key] = value

    applied_overrides: Dict[str, Optional[str]] = {}
    for key, value in overrides.items():
        if key in cloned:
            applied_overrides[key] = value
            cloned[key] = value

    return CloneResult(cloned=cloned, remapped=remapped, overridden=applied_overrides)
