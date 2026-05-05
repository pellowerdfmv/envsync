"""Diff utilities for comparing .env files and reporting differences."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two env variable sets."""

    only_in_source: Set[str] = field(default_factory=set)
    only_in_target: Set[str] = field(default_factory=set)
    value_changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (src_val, tgt_val)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_source or self.only_in_target or self.value_changed)

    def summary(self) -> str:
        lines = []
        for key in sorted(self.only_in_source):
            lines.append(f"  + {key}  (only in source)")
        for key in sorted(self.only_in_target):
            lines.append(f"  - {key}  (only in target)")
        for key in sorted(self.value_changed):
            src, tgt = self.value_changed[key]
            src_display = repr(src) if src is not None else "<empty>"
            tgt_display = repr(tgt) if tgt is not None else "<empty>"
            lines.append(f"  ~ {key}  {src_display} -> {tgt_display}")
        return "\n".join(lines) if lines else "  No differences found."


def diff_envs(
    source: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
    *,
    compare_values: bool = False,
) -> DiffResult:
    """Compare two parsed env dicts.

    Args:
        source: The reference env mapping (e.g. .env.example).
        target: The env mapping to compare against (e.g. .env).
        compare_values: When True, also report keys whose values differ.

    Returns:
        A DiffResult describing the differences.
    """
    result = DiffResult()
    source_keys = set(source.keys())
    target_keys = set(target.keys())

    result.only_in_source = source_keys - target_keys
    result.only_in_target = target_keys - source_keys

    if compare_values:
        for key in source_keys & target_keys:
            if source[key] != target[key]:
                result.value_changed[key] = (source[key], target[key])

    return result
