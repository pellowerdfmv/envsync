"""Key/value transformation utilities for .env mappings."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    original: Dict[str, Optional[str]]
    transformed: Dict[str, Optional[str]]
    applied: List[str] = field(default_factory=list)

    def __len__(self) -> int:  # number of changed entries
        return sum(
            1
            for k in self.original
            if self.original.get(k) != self.transformed.get(k)
        )


def _upper_keys(env: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Return a copy with all keys uppercased."""
    return {k.upper(): v for k, v in env.items()}


def _strip_values(env: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Strip surrounding whitespace from string values."""
    return {k: (v.strip() if isinstance(v, str) else v) for k, v in env.items()}


def _remove_none(env: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Drop keys whose value is None."""
    return {k: v for k, v in env.items() if v is not None}


_BUILTIN: Dict[str, Callable[[Dict[str, Optional[str]]], Dict[str, Optional[str]]]] = {
    "upper_keys": _upper_keys,
    "strip_values": _strip_values,
    "remove_none": _remove_none,
}


def transform_env(
    env: Dict[str, Optional[str]],
    steps: List[str],
) -> TransformResult:
    """Apply a sequence of named transform steps to *env*.

    Parameters
    ----------
    env:   Parsed .env mapping.
    steps: Ordered list of built-in transform names to apply.

    Raises
    ------
    ValueError if an unknown step name is supplied.
    """
    unknown = [s for s in steps if s not in _BUILTIN]
    if unknown:
        raise ValueError(f"Unknown transform steps: {unknown}")

    current = dict(env)
    applied: List[str] = []
    for step in steps:
        current = _BUILTIN[step](current)
        applied.append(step)

    return TransformResult(original=dict(env), transformed=current, applied=applied)
