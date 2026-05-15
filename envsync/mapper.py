"""Map (rename/transform) keys in an env dict using a key mapping table."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from .parser import parse_env_file


@dataclass
class MapResult:
    """Result of a key-mapping operation."""

    mapped: Dict[str, Optional[str]]
    """The env dict with keys replaced according to *mapping*."""

    applied: Dict[str, str]
    """Mapping entries that were actually used  {old_key: new_key}."""

    skipped: Dict[str, str]
    """Mapping entries whose source key was not present  {old_key: new_key}."""

    source_path: Optional[Path] = field(default=None)

    def __len__(self) -> int:  # number of keys in the result env
        return len(self.mapped)

    def has_remaps(self) -> bool:
        """Return True when at least one mapping was applied."""
        return bool(self.applied)

    def summary(self) -> str:
        parts = [f"{len(self.mapped)} key(s)"]
        if self.applied:
            parts.append(f"{len(self.applied)} remapped")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (not found)")
        src = f" ({self.source_path})" if self.source_path else ""
        return ", ".join(parts) + src


def map_env(
    env: Dict[str, Optional[str]],
    mapping: Dict[str, str],
    *,
    source_path: Optional[Path] = None,
) -> MapResult:
    """Return a new env dict with keys renamed according to *mapping*.

    Keys present in *env* but absent from *mapping* are kept unchanged.
    If a *mapping* source key is absent from *env* it is recorded in
    ``MapResult.skipped`` and silently ignored.

    Parameters
    ----------
    env:
        The parsed env dictionary to transform.
    mapping:
        ``{old_key: new_key}`` pairs.
    source_path:
        Optional path stored on the result for reporting purposes.
    """
    applied: Dict[str, str] = {}
    skipped: Dict[str, str] = {}

    # Build reverse lookup so we can detect collisions cleanly.
    result: Dict[str, Optional[str]] = {}

    # Keys that will be renamed — collect them first so we can skip originals.
    rename_sources = set(mapping.keys())

    for key, value in env.items():
        if key in rename_sources:
            new_key = mapping[key]
            result[new_key] = value
            applied[key] = new_key
        else:
            result[key] = value

    for old_key, new_key in mapping.items():
        if old_key not in env:
            skipped[old_key] = new_key

    return MapResult(
        mapped=result,
        applied=applied,
        skipped=skipped,
        source_path=source_path,
    )


def map_env_file(
    path: Path,
    mapping: Dict[str, str],
) -> MapResult:
    """Convenience wrapper: parse *path* then apply :func:`map_env`."""
    env = parse_env_file(path)
    return map_env(env, mapping, source_path=path)
