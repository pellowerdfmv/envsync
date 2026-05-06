"""Merge multiple .env files with configurable precedence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envsync.parser import parse_env_file


@dataclass
class MergeResult:
    """Outcome of merging multiple env files."""

    merged: Dict[str, Optional[str]]
    conflicts: Dict[str, List[Tuple[str, Optional[str]]]]  # key -> [(source, value)]
    sources: List[str]

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        lines = [f"Merged {len(self.sources)} file(s), {len(self.merged)} keys total."]
        if self.conflicts:
            lines.append(f"Conflicts detected in {len(self.conflicts)} key(s):")
            for key, origins in self.conflicts.items():
                detail = ", ".join(f"{src}={val!r}" for src, val in origins)
                lines.append(f"  {key}: {detail}")
        else:
            lines.append("No conflicts.")
        return "\n".join(lines)


def merge_envs(
    *paths: str,
    strategy: str = "last_wins",
) -> MergeResult:
    """Merge env files in order.

    Parameters
    ----------
    *paths:
        Paths to .env files; later files take precedence when strategy is
        ``'last_wins'`` (default).  Use ``'first_wins'`` to keep the first
        seen value.
    strategy:
        ``'last_wins'`` or ``'first_wins'``.
    """
    if strategy not in ("last_wins", "first_wins"):
        raise ValueError(f"Unknown strategy {strategy!r}; use 'last_wins' or 'first_wins'.")

    merged: Dict[str, Optional[str]] = {}
    conflicts: Dict[str, List[Tuple[str, Optional[str]]]] = {}
    seen: Dict[str, Tuple[str, Optional[str]]] = {}  # key -> (first_source, first_value)

    for path in paths:
        env = parse_env_file(path)
        for key, value in env.items():
            if key in seen:
                prev_src, prev_val = seen[key]
                if prev_val != value:
                    if key not in conflicts:
                        conflicts[key] = [(prev_src, prev_val)]
                    conflicts[key].append((path, value))

                if strategy == "last_wins":
                    merged[key] = value
            else:
                seen[key] = (path, value)
                merged[key] = value

    return MergeResult(merged=merged, conflicts=conflicts, sources=list(paths))
