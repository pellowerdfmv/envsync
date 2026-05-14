"""Promote env values from one environment tier to another.

A *promotion* copies keys from a source env (e.g. .env.staging) into a
target env (e.g. .env.production), optionally skipping keys that are
already set in the target.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsync.parser import parse_env_file


@dataclass
class PromoteResult:
    source: str
    target: str
    promoted: Dict[str, Optional[str]] = field(default_factory=dict)
    skipped: Dict[str, Optional[str]] = field(default_factory=dict)
    merged: Dict[str, Optional[str]] = field(default_factory=dict)

    def __len__(self) -> int:  # noqa: D105
        return len(self.promoted)

    def has_promotions(self) -> bool:
        """Return True if at least one key was promoted."""
        return bool(self.promoted)

    def summary(self) -> str:
        """Return a human-readable summary of the promotion."""
        lines: List[str] = [
            f"Promote {self.source} -> {self.target}",
            f"  promoted : {len(self.promoted)}",
            f"  skipped  : {len(self.skipped)}",
        ]
        return "\n".join(lines)


def promote_env(
    source: Path,
    target: Path,
    *,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> PromoteResult:
    """Promote values from *source* into *target*.

    Parameters
    ----------
    source:
        Path to the source .env file (e.g. staging).
    target:
        Path to the target .env file (e.g. production).
    overwrite:
        When *True*, source values overwrite existing target values.
        When *False* (default), keys already present in target are skipped.
    keys:
        Optional allowlist of key names to promote.  When *None* all keys
        from the source are considered.
    """
    src_env = parse_env_file(source)
    tgt_env = parse_env_file(target)

    result = PromoteResult(source=str(source), target=str(target))
    result.merged = dict(tgt_env)

    candidates = {k: v for k, v in src_env.items() if keys is None or k in keys}

    for key, value in candidates.items():
        if key in tgt_env and not overwrite:
            result.skipped[key] = value
        else:
            result.promoted[key] = value
            result.merged[key] = value

    return result
