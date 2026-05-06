"""Profile .env files to produce summary statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from envsync.parser import parse_env_file


@dataclass
class ProfileResult:
    path: str
    total_keys: int = 0
    set_keys: int = 0
    empty_keys: int = 0
    null_keys: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    key_lengths: Dict[str, int] = field(default_factory=dict)

    @property
    def unset_keys(self) -> int:
        """Keys that are either empty or null."""
        return self.empty_keys + self.null_keys

    @property
    def fill_rate(self) -> float:
        """Fraction of keys that have a non-empty, non-null value."""
        if self.total_keys == 0:
            return 0.0
        return self.set_keys / self.total_keys

    def summary(self) -> str:
        lines = [
            f"Profile: {self.path}",
            f"  Total keys   : {self.total_keys}",
            f"  Set          : {self.set_keys}",
            f"  Empty        : {self.empty_keys}",
            f"  Null         : {self.null_keys}",
            f"  Fill rate    : {self.fill_rate:.0%}",
            f"  Comment lines: {self.comment_lines}",
            f"  Blank lines  : {self.blank_lines}",
        ]
        return "\n".join(lines)


def profile_env(path: str) -> ProfileResult:
    """Parse *path* and compute statistics about its contents."""
    result = ProfileResult(path=path)

    env: Dict[str, Optional[str]] = parse_env_file(path)
    result.total_keys = len(env)

    for key, value in env.items():
        result.key_lengths[key] = len(key)
        if value is None:
            result.null_keys += 1
        elif value == "":
            result.empty_keys += 1
        else:
            result.set_keys += 1

    # Count raw comment / blank lines by re-reading the file
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("#"):
                result.comment_lines += 1
            elif stripped == "":
                result.blank_lines += 1

    return result
