"""Split a flat env mapping into multiple env files by key prefix or pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    """Outcome of a split operation."""
    buckets: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)
    unmatched: Dict[str, Optional[str]] = field(default_factory=dict)

    def __len__(self) -> int:  # number of non-empty buckets
        return sum(1 for v in self.buckets.values() if v)

    def summary(self) -> str:
        parts = [f"{name}({len(keys)} keys)" for name, keys in self.buckets.items() if keys]
        unmatched_count = len(self.unmatched)
        base = ", ".join(parts) if parts else "no buckets"
        if unmatched_count:
            return f"{base}; {unmatched_count} unmatched"
        return base


def split_env(
    env: Dict[str, Optional[str]],
    groups: Dict[str, str],
    *,
    default_bucket: Optional[str] = None,
) -> SplitResult:
    """Split *env* into named buckets using regex patterns.

    Parameters
    ----------
    env:
        Flat mapping of key -> value to split.
    groups:
        Mapping of bucket_name -> regex pattern.  Keys whose names match the
        pattern (full-key match via ``re.search``) are placed in that bucket.
        Patterns are evaluated in insertion order; the first match wins.
    default_bucket:
        If provided, unmatched keys are placed in this bucket instead of
        ``SplitResult.unmatched``.

    Returns
    -------
    SplitResult
    """
    compiled = {name: re.compile(pattern) for name, pattern in groups.items()}
    result = SplitResult(buckets={name: {} for name in groups})
    if default_bucket and default_bucket not in result.buckets:
        result.buckets[default_bucket] = {}

    for key, value in env.items():
        placed = False
        for name, regex in compiled.items():
            if regex.search(key):
                result.buckets[name][key] = value
                placed = True
                break
        if not placed:
            if default_bucket is not None:
                result.buckets[default_bucket][key] = value
            else:
                result.unmatched[key] = value

    return result
