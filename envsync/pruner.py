"""pruner.py – remove keys from an env mapping that match given patterns or an explicit list."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .parser import parse_env_file

Env = Dict[str, Optional[str]]


@dataclass
class PruneResult:
    env: Env
    removed_keys: List[str]
    source_path: Optional[Path] = None

    def __len__(self) -> int:  # noqa: D105
        return len(self.env)

    def has_removals(self) -> bool:
        """Return True when at least one key was pruned."""
        return bool(self.removed_keys)

    def summary(self) -> str:
        """Human-readable one-liner."""
        n = len(self.removed_keys)
        src = f" ({self.source_path})" if self.source_path else ""
        if n == 0:
            return f"pruner: no keys removed{src}"
        keys = ", ".join(self.removed_keys)
        return f"pruner: removed {n} key(s){src} – {keys}"


def prune_env(
    env: Env,
    *,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    source_path: Optional[Path] = None,
) -> PruneResult:
    """Return a new env with matching keys removed.

    Args:
        env: The source mapping.
        keys: Exact key names to remove.
        patterns: Regex patterns; any key fully matching a pattern is removed.
        source_path: Optional path recorded in the result for reporting.

    Returns:
        A :class:`PruneResult` containing the pruned mapping and removed key list.
    """
    exact: set[str] = set(keys or [])
    compiled = [re.compile(p) for p in (patterns or [])]

    pruned: Env = {}
    removed: List[str] = []

    for k, v in env.items():
        if k in exact or any(rx.fullmatch(k) for rx in compiled):
            removed.append(k)
        else:
            pruned[k] = v

    return PruneResult(env=pruned, removed_keys=removed, source_path=source_path)


def prune_file(
    path: Path,
    *,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> PruneResult:
    """Parse *path* and prune it in one step."""
    env = parse_env_file(path)
    return prune_env(env, keys=keys, patterns=patterns, source_path=path)
