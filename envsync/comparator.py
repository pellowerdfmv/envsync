"""Compare multiple .env files and produce a unified comparison matrix."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envsync.parser import parse_env_file


@dataclass
class CompareResult:
    """Holds the result of comparing N env files."""

    files: List[str]
    all_keys: Set[str]
    matrix: Dict[str, Dict[str, Optional[str]]]  # key -> {filename -> value}
    common_keys: Set[str] = field(default_factory=set)
    unique_keys: Dict[str, Set[str]] = field(default_factory=dict)  # filename -> keys only in that file

    def keys_missing_in(self, filename: str) -> Set[str]:
        """Return keys present in other files but absent in *filename*."""
        return {
            key
            for key, file_map in self.matrix.items()
            if filename not in file_map
        }

    def value_conflicts(self) -> Dict[str, List[str]]:
        """Return keys whose values differ across files that define them."""
        conflicts: Dict[str, List[str]] = {}
        for key, file_map in self.matrix.items():
            values = list(file_map.values())
            if len(set(v for v in values if v is not None)) > 1:
                conflicts[key] = [f"{f}={v!r}" for f, v in file_map.items()]
        return conflicts


def compare_envs(paths: List[str]) -> CompareResult:
    """Parse each path and build a unified comparison matrix."""
    if not paths:
        raise ValueError("At least one path must be provided.")

    parsed: Dict[str, Dict[str, Optional[str]]] = {
        p: parse_env_file(p) for p in paths
    }

    all_keys: Set[str] = set()
    for env in parsed.values():
        all_keys.update(env.keys())

    matrix: Dict[str, Dict[str, Optional[str]]] = {key: {} for key in all_keys}
    for path, env in parsed.items():
        for key, value in env.items():
            matrix[key][path] = value

    common_keys = {
        key for key, file_map in matrix.items() if len(file_map) == len(paths)
    }

    unique_keys: Dict[str, Set[str]] = {p: set() for p in paths}
    for key, file_map in matrix.items():
        if len(file_map) == 1:
            only_file = next(iter(file_map))
            unique_keys[only_file].add(key)

    return CompareResult(
        files=list(paths),
        all_keys=all_keys,
        matrix=matrix,
        common_keys=common_keys,
        unique_keys=unique_keys,
    )
