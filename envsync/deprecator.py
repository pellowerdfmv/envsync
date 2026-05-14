"""deprecator.py – mark and report deprecated keys in an env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsync.parser import parse_env_file


@dataclass
class DeprecateResult:
    """Outcome of a deprecation scan."""

    env: Dict[str, Optional[str]]
    deprecated: Dict[str, str]          # key -> deprecation message
    present: List[str]                  # deprecated keys that were found
    absent: List[str]                   # deprecated keys not in env
    source_path: Optional[Path] = None

    # ------------------------------------------------------------------
    def __len__(self) -> int:           # number of keys in env
        return len(self.env)

    def has_deprecated(self) -> bool:
        """Return True if any deprecated keys are present."""
        return bool(self.present)

    def summary(self) -> str:
        total = len(self.deprecated)
        found = len(self.present)
        src = f" ({self.source_path})" if self.source_path else ""
        return (
            f"Deprecation scan{src}: {found}/{total} deprecated key(s) present."
        )


def deprecate_env(
    env: Dict[str, Optional[str]],
    deprecated: Dict[str, str],
    *,
    remove: bool = False,
    source_path: Optional[Path] = None,
) -> DeprecateResult:
    """Scan *env* for deprecated keys.

    Parameters
    ----------
    env:
        Parsed environment mapping.
    deprecated:
        Mapping of ``{key: deprecation_message}``.
    remove:
        When *True*, deprecated keys are removed from the returned ``env``.
    source_path:
        Optional origin path stored in the result for display purposes.
    """
    present: List[str] = []
    absent: List[str] = []

    for key in deprecated:
        if key in env:
            present.append(key)
        else:
            absent.append(key)

    result_env = dict(env)
    if remove:
        for key in present:
            del result_env[key]

    return DeprecateResult(
        env=result_env,
        deprecated=deprecated,
        present=sorted(present),
        absent=sorted(absent),
        source_path=source_path,
    )


def deprecate_file(
    path: Path,
    deprecated: Dict[str, str],
    *,
    remove: bool = False,
) -> DeprecateResult:
    """Convenience wrapper that parses *path* before scanning."""
    env = parse_env_file(path)
    return deprecate_env(env, deprecated, remove=remove, source_path=path)
