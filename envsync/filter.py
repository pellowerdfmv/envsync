"""Filter .env entries by key pattern, prefix, or value presence."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, Optional[str]]
    excluded: Dict[str, Optional[str]]
    pattern: str

    def __len__(self) -> int:
        return len(self.matched)

    def summary(self) -> str:
        total = len(self.matched) + len(self.excluded)
        return (
            f"Filter '{self.pattern}': {len(self.matched)}/{total} keys matched."
        )


def filter_env(
    env: Dict[str, Optional[str]],
    *,
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
    set_only: bool = False,
    unset_only: bool = False,
) -> FilterResult:
    """Return a FilterResult partitioning *env* into matched / excluded.

    Parameters
    ----------
    env:        Parsed env mapping (key -> value | None).
    pattern:    Regex applied to key names.  Matched when the pattern is found
                anywhere in the key (re.search).
    prefix:     If given, only keys that start with this string are kept.
                Applied after *pattern*.
    set_only:   Keep only keys whose value is not None and not empty.
    unset_only: Keep only keys whose value is None.
    """
    if set_only and unset_only:
        raise ValueError("set_only and unset_only are mutually exclusive")

    label_parts: List[str] = []
    if pattern:
        label_parts.append(f"re:{pattern}")
    if prefix:
        label_parts.append(f"prefix:{prefix}")
    if set_only:
        label_parts.append("set_only")
    if unset_only:
        label_parts.append("unset_only")
    label = ",".join(label_parts) or "*"

    compiled = re.compile(pattern) if pattern else None

    matched: Dict[str, Optional[str]] = {}
    excluded: Dict[str, Optional[str]] = {}

    for key, value in env.items():
        keep = True
        if compiled and not compiled.search(key):
            keep = False
        if keep and prefix and not key.startswith(prefix):
            keep = False
        if keep and set_only and not value:
            keep = False
        if keep and unset_only and value is not None:
            keep = False

        if keep:
            matched[key] = value
        else:
            excluded[key] = value

    return FilterResult(matched=matched, excluded=excluded, pattern=label)
