"""aliaser.py – create aliased copies of env keys.

Allows mapping existing keys to new names while keeping the originals,
or replacing them entirely.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AliasResult:
    env: Dict[str, Optional[str]]
    aliased: Dict[str, str]   # new_key -> original_key
    missing: list[str]        # requested originals that were not found

    def __len__(self) -> int:  # noqa: D105
        return len(self.env)

    def has_missing(self) -> bool:
        """Return True when at least one source key was absent."""
        return bool(self.missing)

    def summary(self) -> str:
        """Human-readable one-liner."""
        parts = [f"{len(self.aliased)} alias(es) created"]
        if self.missing:
            parts.append(f"{len(self.missing)} source key(s) not found")
        return "; ".join(parts)


def alias_env(
    env: Dict[str, Optional[str]],
    aliases: Dict[str, str],
    *,
    keep_original: bool = True,
) -> AliasResult:
    """Create aliased keys in *env*.

    Parameters
    ----------
    env:
        Source environment mapping.
    aliases:
        Mapping of ``{new_key: original_key}``.
    keep_original:
        When *True* (default) the original key is preserved alongside the
        alias.  When *False* the original key is removed.

    Returns
    -------
    AliasResult
    """
    result: Dict[str, Optional[str]] = dict(env)
    aliased: Dict[str, str] = {}
    missing: list[str] = []

    for new_key, src_key in aliases.items():
        if src_key not in env:
            missing.append(src_key)
            continue
        result[new_key] = env[src_key]
        aliased[new_key] = src_key
        if not keep_original:
            result.pop(src_key, None)

    return AliasResult(env=result, aliased=aliased, missing=missing)
