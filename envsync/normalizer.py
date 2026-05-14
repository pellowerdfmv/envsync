"""Normalize .env key names to a canonical form."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .parser import parse_env_file


@dataclass
class NormalizeResult:
    """Outcome of a normalize operation."""

    normalized: Dict[str, Optional[str]]
    renamed: List[Tuple[str, str]]  # (original, canonical)
    source_path: Optional[Path] = None

    def __len__(self) -> int:  # noqa: D105
        return len(self.normalized)

    @property
    def has_changes(self) -> bool:
        """Return True if any keys were renamed."""
        return bool(self.renamed)

    def summary(self) -> str:
        """Human-readable summary."""
        src = f" ({self.source_path})" if self.source_path else ""
        if not self.has_changes:
            return f"normalize: no changes{src} — {len(self)} keys already canonical"
        return (
            f"normalize: {len(self.renamed)} key(s) renamed{src} "
            f"— {len(self)} total keys"
        )


def _canonical(key: str) -> str:
    """Return the canonical form of *key*: upper-case, spaces/hyphens → underscore."""
    return key.strip().upper().replace("-", "_").replace(" ", "_")


def normalize_env(
    env: Dict[str, Optional[str]],
    *,
    source_path: Optional[Path] = None,
) -> NormalizeResult:
    """Normalize every key in *env* to its canonical form.

    When two keys collapse to the same canonical form the *last* one wins
    (preserving insertion order behaviour consistent with the rest of the
    project).
    """
    normalized: Dict[str, Optional[str]] = {}
    renamed: List[Tuple[str, str]] = []

    for original_key, value in env.items():
        canon = _canonical(original_key)
        if canon != original_key:
            renamed.append((original_key, canon))
        normalized[canon] = value

    return NormalizeResult(
        normalized=normalized,
        renamed=renamed,
        source_path=source_path,
    )


def normalize_file(path: Path) -> NormalizeResult:
    """Parse *path* and return a :class:`NormalizeResult`."""
    env = parse_env_file(path)
    return normalize_env(env, source_path=path)
