"""Multi-file diff: compare N env files against a reference."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsync.parser import parse_env_file
from envsync.differ import diff_envs, DiffResult


@dataclass
class MultiDiffEntry:
    """Diff result for one target file against the reference."""

    target_path: Path
    result: DiffResult


@dataclass
class MultiDiffResult:
    """Aggregated diff of multiple files against a single reference."""

    reference_path: Path
    entries: List[MultiDiffEntry] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    def has_differences(self) -> bool:
        return any(e.result.has_differences() for e in self.entries)

    def __len__(self) -> int:
        """Number of target files compared."""
        return len(self.entries)

    def summary(self) -> str:
        lines: List[str] = [
            f"Reference: {self.reference_path}",
            f"Targets compared: {len(self)}",
        ]
        for entry in self.entries:
            status = "differs" if entry.result.has_differences() else "in sync"
            lines.append(f"  {entry.target_path}: {status}")
            sub = entry.result.summary()
            if sub:
                for sub_line in sub.splitlines():
                    lines.append(f"    {sub_line}")
        return "\n".join(lines)


def diff_multi(
    reference: Path,
    targets: List[Path],
    *,
    compare_values: bool = False,
) -> MultiDiffResult:
    """Diff every file in *targets* against *reference*.

    Parameters
    ----------
    reference:
        The canonical env file used as the source of truth.
    targets:
        One or more env files to compare against *reference*.
    compare_values:
        When ``True`` value differences are included in each DiffResult.
    """
    ref_env = parse_env_file(reference)
    multi = MultiDiffResult(reference_path=reference)

    for target in targets:
        target_env = parse_env_file(target)
        result = diff_envs(
            ref_env,
            target_env,
            source_path=reference,
            target_path=target,
            compare_values=compare_values,
        )
        multi.entries.append(MultiDiffEntry(target_path=target, result=result))

    return multi
