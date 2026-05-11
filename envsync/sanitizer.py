"""sanitizer.py – strip, normalise, and clean env key/value pairs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SanitizeResult:
    env: Dict[str, Optional[str]]
    cleaned: List[Tuple[str, str]]  # (key, description) of every change made

    def __len__(self) -> int:  # noqa: D105
        return len(self.env)

    def has_changes(self) -> bool:
        """Return True when at least one sanitization change was applied."""
        return bool(self.cleaned)

    def summary(self) -> str:
        """Human-readable summary of sanitization changes."""
        if not self.cleaned:
            return "No sanitization changes applied."
        lines = [f"Sanitized {len(self.cleaned)} change(s):"]
        for key, desc in self.cleaned:
            lines.append(f"  {key}: {desc}")
        return "\n".join(lines)


def _sanitize_key(raw: str) -> Tuple[str, List[str]]:
    """Return (normalised_key, list_of_descriptions)."""
    descriptions: List[str] = []
    key = raw.strip()
    if key != raw:
        descriptions.append("stripped surrounding whitespace from key")
    upper = key.upper()
    if upper != key:
        descriptions.append("uppercased key")
        key = upper
    # Replace hyphens with underscores
    clean = key.replace("-", "_")
    if clean != key:
        descriptions.append("replaced hyphens with underscores in key")
        key = clean
    return key, descriptions


def _sanitize_value(raw: Optional[str]) -> Tuple[Optional[str], List[str]]:
    """Return (normalised_value, list_of_descriptions)."""
    if raw is None:
        return None, []
    descriptions: List[str] = []
    value = raw.strip()
    if value != raw:
        descriptions.append("stripped surrounding whitespace from value")
    if value == "":
        return None, descriptions + ["converted empty string to None"]
    return value, descriptions


def sanitize_env(
    env: Dict[str, Optional[str]],
    *,
    fix_keys: bool = True,
    fix_values: bool = True,
) -> SanitizeResult:
    """Sanitize *env*, returning a new cleaned mapping and a change log.

    Parameters
    ----------
    env:        Raw environment mapping.
    fix_keys:   Uppercase keys, strip whitespace, replace hyphens.
    fix_values: Strip whitespace from values; convert empty strings to None.
    """
    result: Dict[str, Optional[str]] = {}
    cleaned: List[Tuple[str, str]] = []

    for raw_key, raw_value in env.items():
        key = raw_key
        if fix_keys:
            key, key_descs = _sanitize_key(raw_key)
            for desc in key_descs:
                cleaned.append((raw_key, desc))

        value = raw_value
        if fix_values:
            value, val_descs = _sanitize_value(raw_value)
            for desc in val_descs:
                cleaned.append((key, desc))

        result[key] = value

    return SanitizeResult(env=result, cleaned=cleaned)
