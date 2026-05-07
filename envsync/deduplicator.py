"""Detect and remove duplicate keys within a single .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsync.parser import parse_env_file


@dataclass
class DeduplicateResult:
    """Outcome of a deduplication pass over an env file."""

    path: Path
    original: Dict[str, Optional[str]]
    deduped: Dict[str, Optional[str]]
    duplicates: Dict[str, List[Optional[str]]]  # key -> all values seen (in order)

    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def __len__(self) -> int:
        """Return the number of keys that had duplicates."""
        return len(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates():
            return f"{self.path}: no duplicate keys found."
        lines = [f"{self.path}: {len(self.duplicates)} duplicate key(s) found."]
        for key, values in self.duplicates.items():
            rendered = ", ".join(repr(v) for v in values)
            lines.append(f"  {key}: [{rendered}]")
        return "\n".join(lines)


def deduplicate_env(path: Path, strategy: str = "last") -> DeduplicateResult:
    """Parse *path* and collapse any keys that appear more than once.

    Parameters
    ----------
    path:
        Path to the .env file to inspect.
    strategy:
        ``"last"`` (default) keeps the final occurrence of a duplicated key;
        ``"first"`` keeps the first occurrence.

    Returns
    -------
    DeduplicateResult
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy {strategy!r}. Use 'first' or 'last'.")

    raw_lines: List[tuple[str, Optional[str]]] = []
    seen: Dict[str, List[Optional[str]]] = {}

    # Re-parse manually to detect duplicate keys (parse_env_file collapses them)
    with path.open() as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, _, raw_val = stripped.partition("=")
            key = key.strip()
            value: Optional[str] = raw_val.strip() or None
            raw_lines.append((key, value))
            seen.setdefault(key, []).append(value)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    original = parse_env_file(path)

    # Build deduplicated mapping respecting chosen strategy
    if strategy == "first":
        deduped: Dict[str, Optional[str]] = {}
        for key, value in raw_lines:
            if key not in deduped:
                deduped[key] = value
    else:  # last
        deduped = {}
        for key, value in raw_lines:
            deduped[key] = value

    return DeduplicateResult(
        path=path,
        original=original,
        deduped=deduped,
        duplicates=duplicates,
    )
