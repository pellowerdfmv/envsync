"""stamper.py — Attach metadata stamps (author, date, version) to env mappings."""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class StampResult:
    env: Dict[str, Optional[str]]
    stamps: Dict[str, str]
    source_path: Optional[str] = None

    def __len__(self) -> int:
        return len(self.stamps)

    def has_stamps(self) -> bool:
        return bool(self.stamps)

    def summary(self) -> str:
        parts = [f"StampResult: {len(self.stamps)} stamp(s) applied"]
        if self.source_path:
            parts.append(f"({self.source_path})")
        return " ".join(parts)


def stamp_env(
    env: Dict[str, Optional[str]],
    *,
    author: Optional[str] = None,
    version: Optional[str] = None,
    date: Optional[str] = None,
    prefix: str = "ENVSYNC",
    overwrite: bool = True,
    source_path: Optional[str] = None,
) -> StampResult:
    """Return a copy of *env* with metadata stamp keys injected.

    Parameters
    ----------
    env:        Source environment mapping.
    author:     Value for ``<PREFIX>_AUTHOR``.  Omitted when *None*.
    version:    Value for ``<PREFIX>_VERSION``.  Omitted when *None*.
    date:       Value for ``<PREFIX>_DATE``.  Defaults to today (ISO-8601)
                when the caller passes the sentinel string ``"auto"``.
    prefix:     Key prefix used for all stamp keys (default ``ENVSYNC``).
    overwrite:  When *False*, existing keys are not replaced.
    source_path: Optional path label stored on the result.
    """
    result: Dict[str, Optional[str]] = dict(env)
    stamps: Dict[str, str] = {}

    candidates: Dict[str, Optional[str]] = {}
    if author is not None:
        candidates[f"{prefix}_AUTHOR"] = author
    if version is not None:
        candidates[f"{prefix}_VERSION"] = version
    if date is not None:
        resolved_date = (
            datetime.date.today().isoformat() if date == "auto" else date
        )
        candidates[f"{prefix}_DATE"] = resolved_date

    for key, value in candidates.items():
        if not overwrite and key in result:
            continue
        result[key] = value
        stamps[key] = value  # type: ignore[assignment]

    return StampResult(env=result, stamps=stamps, source_path=source_path)
