"""Rename keys across an env mapping with optional conflict detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameResult:
    renamed: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    skipped: List[str] = field(default_factory=list)         # keys not found in env
    conflicts: List[str] = field(default_factory=list)       # new_key already exists
    env: Dict[str, Optional[str]] = field(default_factory=dict)


def has_conflicts(result: RenameResult) -> bool:
    return bool(result.conflicts)


def summary(result: RenameResult) -> str:
    parts: List[str] = []
    if result.renamed:
        pairs = ", ".join(f"{o} -> {n}" for o, n in result.renamed.items())
        parts.append(f"Renamed: {pairs}")
    if result.skipped:
        parts.append(f"Skipped (not found): {', '.join(result.skipped)}")
    if result.conflicts:
        parts.append(f"Conflicts (target key exists): {', '.join(result.conflicts)}")
    return "; ".join(parts) if parts else "No renames performed."


def rename_keys(
    env: Dict[str, Optional[str]],
    renames: Dict[str, str],
    overwrite: bool = False,
) -> RenameResult:
    """Return a new env dict with keys renamed according to *renames* mapping.

    Parameters
    ----------
    env:
        Source environment mapping.
    renames:
        ``{old_key: new_key}`` pairs to apply.
    overwrite:
        When *True*, silently overwrite an existing *new_key*.  When *False*
        (default) the rename is skipped and recorded in ``conflicts``.
    """
    result = RenameResult(env=dict(env))

    for old_key, new_key in renames.items():
        if old_key not in result.env:
            result.skipped.append(old_key)
            continue

        if new_key in result.env and not overwrite:
            result.conflicts.append(new_key)
            continue

        value = result.env.pop(old_key)
        result.env[new_key] = value
        result.renamed[old_key] = new_key

    return result
