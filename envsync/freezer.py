"""freezer.py — Freeze an env dict so values cannot be overwritten accidentally.

A frozen env is a read-only snapshot represented as an immutable mapping.
The module also provides helpers to detect which keys changed between a
live env dict and its frozen counterpart.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Mapping, Optional


@dataclass(frozen=True)
class FreezeResult:
    """Outcome of a freeze operation."""

    frozen: Mapping[str, Optional[str]]
    """Immutable view of the env at freeze time."""

    source_path: str = ""
    """Optional path the env was loaded from."""

    changed_keys: tuple = field(default_factory=tuple)
    """Keys whose values differ between *frozen* and a later comparison env."""

    def __len__(self) -> int:  # pragma: no cover
        return len(self.frozen)

    def has_changes(self) -> bool:
        """Return True if any key differs from the frozen baseline."""
        return len(self.changed_keys) > 0

    def summary(self) -> str:
        """Human-readable one-liner."""
        n = len(self.frozen)
        c = len(self.changed_keys)
        if c == 0:
            return f"Frozen {n} key(s) — no drift detected."
        keys = ", ".join(self.changed_keys)
        return f"Frozen {n} key(s) — {c} key(s) drifted: {keys}"


def freeze_env(
    env: Dict[str, Optional[str]],
    *,
    source_path: str = "",
) -> FreezeResult:
    """Freeze *env* into an immutable mapping.

    Parameters
    ----------
    env:
        The parsed env dictionary to freeze.
    source_path:
        Optional file path stored for reference.

    Returns
    -------
    FreezeResult
        Contains the frozen mapping and metadata.
    """
    frozen: Mapping[str, Optional[str]] = MappingProxyType(dict(env))
    return FreezeResult(frozen=frozen, source_path=source_path)


def detect_drift(
    result: FreezeResult,
    current: Dict[str, Optional[str]],
) -> FreezeResult:
    """Compare *current* env against the frozen baseline in *result*.

    Returns a **new** FreezeResult with ``changed_keys`` populated for
    every key whose value differs (including keys added or removed).
    """
    baseline = result.frozen
    all_keys = set(baseline) | set(current)
    changed = tuple(
        k for k in sorted(all_keys) if baseline.get(k) != current.get(k)
    )
    return FreezeResult(
        frozen=result.frozen,
        source_path=result.source_path,
        changed_keys=changed,
    )
