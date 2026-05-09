"""Flatten nested key structures by expanding delimiter-separated keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    """Result of a flatten operation."""

    original: Dict[str, Optional[str]]
    flattened: Dict[str, Optional[str]]
    expanded: List[str] = field(default_factory=list)
    delimiter: str = "__"

    def __len__(self) -> int:
        return len(self.flattened)

    def has_expansions(self) -> bool:
        """Return True if any keys were expanded during flattening."""
        return bool(self.expanded)

    def summary(self) -> str:
        """Return a human-readable summary of the flatten operation."""
        total = len(self.flattened)
        exp = len(self.expanded)
        if not exp:
            return f"{total} key(s) — no expansions performed."
        return (
            f"{total} key(s) total; {exp} key(s) expanded "
            f"using delimiter '{self.delimiter}'."
        )


def _expand_key(
    key: str, value: Optional[str], delimiter: str
) -> Dict[str, Optional[str]]:
    """Split a key on *delimiter* and return a dict with the leaf key."""
    parts = key.split(delimiter)
    leaf = "_".join(parts)  # join segments with single underscore
    return {leaf: value}


def flatten_env(
    env: Dict[str, Optional[str]],
    delimiter: str = "__",
    expand: bool = True,
) -> FlattenResult:
    """Flatten *env* by collapsing delimiter-separated key segments.

    Parameters
    ----------
    env:
        Mapping of key → value (values may be ``None``).
    delimiter:
        Segment separator used to detect compound keys (default ``"__"``).
    expand:
        When *True* (default), compound keys are collapsed to a single
        underscore-joined key.  When *False* the original keys are kept.
    """
    flattened: Dict[str, Optional[str]] = {}
    expanded: List[str] = []

    for key, value in env.items():
        if expand and delimiter in key:
            new_key = "_".join(key.split(delimiter))
            flattened[new_key] = value
            expanded.append(key)
        else:
            flattened[key] = value

    return FlattenResult(
        original=dict(env),
        flattened=flattened,
        expanded=expanded,
        delimiter=delimiter,
    )
