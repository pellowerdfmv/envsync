"""Resolve environment variables from multiple sources with priority ordering."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from envsync.parser import parse_env_file


@dataclass
class ResolveResult:
    """Outcome of resolving env vars from multiple sources."""

    resolved: Dict[str, Optional[str]] = field(default_factory=dict)
    sources: Dict[str, str] = field(default_factory=dict)  # key -> source path
    overrides: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old_src, new_src)

    def __len__(self) -> int:  # pragma: no cover
        return len(self.resolved)


def has_overrides(result: ResolveResult) -> bool:
    """Return True when at least one key was overridden by a higher-priority source."""
    return bool(result.overrides)


def summary(result: ResolveResult) -> str:
    """Return a human-readable summary of the resolution."""
    lines = [
        f"Resolved {len(result.resolved)} key(s) from {len(set(result.sources.values()))} source(s).",
    ]
    if result.overrides:
        lines.append(f"{len(result.overrides)} key(s) overridden by higher-priority sources:")
        for key, old_src, new_src in result.overrides:
            lines.append(f"  {key}: {old_src} -> {new_src}")
    return "\n".join(lines)


def resolve_envs(paths: List[Path], *, reverse_priority: bool = False) -> ResolveResult:
    """Resolve env vars from *paths* in priority order.

    By default the **last** path in the list wins (highest priority).  Pass
    ``reverse_priority=True`` to make the **first** path win instead.

    Parameters
    ----------
    paths:
        Ordered list of .env file paths to merge.
    reverse_priority:
        When True the first file takes precedence over later ones.
    """
    result = ResolveResult()

    ordered = list(reversed(paths)) if reverse_priority else paths

    for path in ordered:
        env = parse_env_file(path)
        src = str(path)
        for key, value in env.items():
            if key in result.resolved:
                old_src = result.sources[key]
                result.overrides.append((key, old_src, src))
            result.resolved[key] = value
            result.sources[key] = src

    return result
