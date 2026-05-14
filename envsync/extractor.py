"""Extract a subset of keys from an env mapping into a new mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .parser import parse_env_file


@dataclass
class ExtractResult:
    """Result of an extraction operation."""

    extracted: Dict[str, Optional[str]]
    missing: List[str]
    source_path: Optional[Path] = None

    def __len__(self) -> int:  # noqa: D105
        return len(self.extracted)

    def has_missing(self) -> bool:
        """Return True when one or more requested keys were absent from the source."""
        return bool(self.missing)

    def summary(self) -> str:
        """Return a human-readable summary of the extraction."""
        src = f" ({self.source_path})" if self.source_path else ""
        parts = [f"Extracted {len(self.extracted)} key(s){src}."]
        if self.missing:
            missing_list = ", ".join(self.missing)
            parts.append(f"Missing {len(self.missing)} key(s): {missing_list}.")
        return " ".join(parts)


def extract_env(
    env: Dict[str, Optional[str]],
    keys: List[str],
    *,
    strict: bool = False,
    source_path: Optional[Path] = None,
) -> ExtractResult:
    """Extract *keys* from *env*, returning an :class:`ExtractResult`.

    Parameters
    ----------
    env:
        Source mapping to extract from.
    keys:
        Keys to extract.
    strict:
        When ``True``, raise :class:`KeyError` if any requested key is absent.
    source_path:
        Optional path recorded in the result for reporting purposes.
    """
    extracted: Dict[str, Optional[str]] = {}
    missing: List[str] = []

    for key in keys:
        if key in env:
            extracted[key] = env[key]
        else:
            if strict:
                raise KeyError(f"Key {key!r} not found in env.")
            missing.append(key)

    return ExtractResult(extracted=extracted, missing=missing, source_path=source_path)


def extract_env_file(
    path: Path,
    keys: List[str],
    *,
    strict: bool = False,
) -> ExtractResult:
    """Parse *path* and extract *keys* from the resulting mapping."""
    env = parse_env_file(path)
    return extract_env(env, keys, strict=strict, source_path=path)
