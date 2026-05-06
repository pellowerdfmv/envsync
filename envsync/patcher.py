"""Patch specific keys in an env mapping and report what changed."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PatchResult:
    """Outcome of a patch operation."""

    patched: Dict[str, Optional[str]] = field(default_factory=dict)
    applied: List[Tuple[str, Optional[str], Optional[str]]] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        """Return True when at least one key was updated."""
        return bool(self.applied)

    def summary(self) -> str:
        """Human-readable summary of the patch."""
        lines: List[str] = []
        if self.applied:
            lines.append(f"{len(self.applied)} key(s) patched:")
            for key, old, new in self.applied:
                old_repr = repr(old) if old is not None else "<unset>"
                new_repr = repr(new) if new is not None else "<unset>"
                lines.append(f"  {key}: {old_repr} -> {new_repr}")
        else:
            lines.append("No keys patched.")
        if self.skipped:
            lines.append(f"{len(self.skipped)} key(s) skipped (not present): {', '.join(self.skipped)}")
        return "\n".join(lines)


def patch_env(
    env: Dict[str, Optional[str]],
    patches: Dict[str, Optional[str]],
    *,
    add_missing: bool = False,
) -> PatchResult:
    """Apply *patches* to *env* and return a :class:`PatchResult`.

    Parameters
    ----------
    env:
        Source mapping to patch (not mutated).
    patches:
        Keys and their new values to apply.
    add_missing:
        When *True*, keys absent from *env* are added; otherwise they are
        recorded in :attr:`PatchResult.skipped`.
    """
    result_env = dict(env)
    applied: List[Tuple[str, Optional[str], Optional[str]]] = []
    skipped: List[str] = []

    for key, new_value in patches.items():
        if key in result_env:
            old_value = result_env[key]
            result_env[key] = new_value
            applied.append((key, old_value, new_value))
        elif add_missing:
            result_env[key] = new_value
            applied.append((key, None, new_value))
        else:
            skipped.append(key)

    return PatchResult(patched=result_env, applied=applied, skipped=skipped)
