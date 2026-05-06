"""Compose multiple envsync operations into a single pipeline pass."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsync.linter import LintResult, lint_file
from envsync.auditor import AuditResult, audit_env
from envsync.transformer import TransformResult, transform_env


@dataclass
class PipelineResult:
    path: str
    lint: LintResult
    audit: AuditResult
    transform: TransformResult
    transform_steps: List[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return self.lint.has_issues or self.audit.has_issues

    def summary(self) -> str:
        parts: List[str] = [f"Pipeline report for {self.path}"]
        lint_errors = len(self.lint.errors)
        lint_warns = len(self.lint.warnings)
        audit_errors = len(self.audit.errors)
        audit_warns = len(self.audit.warnings)
        parts.append(
            f"  Lint   : {lint_errors} error(s), {lint_warns} warning(s)"
        )
        parts.append(
            f"  Audit  : {audit_errors} error(s), {audit_warns} warning(s)"
        )
        changed = len(self.transform)
        parts.append(
            f"  Transform ({', '.join(self.transform_steps) or 'none'}): "
            f"{changed} key(s) changed"
        )
        return "\n".join(parts)


def run_pipeline(
    path: str,
    env: Dict[str, Optional[str]],
    transform_steps: Optional[List[str]] = None,
) -> PipelineResult:
    """Run lint → audit → transform on *env* loaded from *path*.

    Parameters
    ----------
    path:             File path (used for lint; must exist on disk).
    env:              Pre-parsed mapping of the file.
    transform_steps:  Ordered transform step names (default: none).
    """
    steps = transform_steps or []

    lint_result = lint_file(path)
    audit_result = audit_env(env)
    transform_result = transform_env(env, steps)

    return PipelineResult(
        path=path,
        lint=lint_result,
        audit=audit_result,
        transform=transform_result,
        transform_steps=steps,
    )
