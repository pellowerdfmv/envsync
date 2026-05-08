"""Pin specific env keys to exact values, producing a locked snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinResult:
    """Outcome of a pin operation."""

    pinned: Dict[str, Optional[str]] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)  # keys not found in env
    source_path: str = ""

    def __len__(self) -> int:  # noqa: D105
        return len(self.pinned)

    def has_skipped(self) -> bool:
        """Return True if any requested keys were absent from the env."""
        return bool(self.skipped)

    def summary(self) -> str:
        """Human-readable one-liner."""
        parts = [f"{len(self.pinned)} key(s) pinned"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (not found)")
        return ", ".join(parts) + f" in {self.source_path or 'env'}"


def pin_env(
    env: Dict[str, Optional[str]],
    pins: Dict[str, Optional[str]],
    *,
    source_path: str = "",
    allow_new: bool = False,
) -> PinResult:
    """Apply *pins* onto *env*, returning a new dict with pinned values.

    Parameters
    ----------
    env:
        The parsed environment mapping to update.
    pins:
        Mapping of key -> forced value to apply.
    source_path:
        Optional label used in the summary.
    allow_new:
        When *True*, keys present in *pins* but absent from *env* are added.
        When *False* (default) such keys are recorded in ``PinResult.skipped``.
    """
    result = PinResult(source_path=source_path)

    for key, value in pins.items():
        if key not in env and not allow_new:
            result.skipped.append(key)
            continue
        result.pinned[key] = value

    merged = dict(env)
    merged.update(result.pinned)
    result.pinned = {k: merged[k] for k in result.pinned}  # keep only pinned slice
    # Attach the full merged env so callers can use it directly
    result._merged: Dict[str, Optional[str]] = merged  # type: ignore[attr-defined]

    return result
