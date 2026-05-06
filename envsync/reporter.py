"""Human-readable report generation combining validation and diff results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envsync.validator import ValidationResult
from envsync.differ import DiffResult


@dataclass
class Report:
    """Aggregated report produced from a validation and/or diff pass."""

    source_file: str
    target_file: str
    validation: Optional[ValidationResult] = None
    diff: Optional[DiffResult] = None
    _lines: List[str] = field(default_factory=list, init=False, repr=False)

    def _build(self) -> None:
        self._lines = []
        self._lines.append(f"=== EnvSync Report ===")
        self._lines.append(f"  Source : {self.source_file}")
        self._lines.append(f"  Target : {self.target_file}")

        if self.validation is not None:
            self._lines.append("")
            self._lines.append("[Validation]")
            self._lines.append(
                f"  Status  : {'PASS' if self.validation.is_valid else 'FAIL'}"
            )
            if self.validation.missing_keys:
                self._lines.append(
                    f"  Missing : {', '.join(sorted(self.validation.missing_keys))}"
                )
            if self.validation.extra_keys:
                self._lines.append(
                    f"  Extra   : {', '.join(sorted(self.validation.extra_keys))}"
                )

        if self.diff is not None:
            self._lines.append("")
            self._lines.append("[Diff]")
            self._lines.append(
                f"  Differences : {'yes' if self.diff.has_differences else 'no'}"
            )
            if self.diff.only_in_source:
                self._lines.append(
                    f"  Only source : {', '.join(sorted(self.diff.only_in_source))}"
                )
            if self.diff.only_in_target:
                self._lines.append(
                    f"  Only target : {', '.join(sorted(self.diff.only_in_target))}"
                )
            if self.diff.value_diffs:
                self._lines.append("  Value diffs :")
                for key in sorted(self.diff.value_diffs):
                    src_v, tgt_v = self.diff.value_diffs[key]
                    self._lines.append(f"    {key}: {src_v!r} -> {tgt_v!r}")

    def render(self) -> str:
        """Return the full report as a string."""
        self._build()
        return "\n".join(self._lines)

    def has_issues(self) -> bool:
        """Return True when any validation or diff issues were found."""
        val_fail = self.validation is not None and not self.validation.is_valid
        diff_fail = self.diff is not None and self.diff.has_differences
        return val_fail or diff_fail
