"""Audit .env files for common security and quality issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Patterns that suggest a value is a placeholder / example
_PLACEHOLDER_HINTS = ("changeme", "example", "your_", "<", ">", "todo", "fixme", "xxx")

# Keys that should never have empty/None values in production
_REQUIRED_NONEMPTY = ("SECRET", "KEY", "PASSWORD", "TOKEN", "DSN", "DATABASE_URL")


@dataclass
class AuditIssue:
    key: str
    message: str
    severity: str  # "warning" | "error"


@dataclass
class AuditResult:
    path: str
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        if not self.has_issues:
            return f"{self.path}: no issues found"
        lines = [f"{self.path}: {len(self.issues)} issue(s)"]
        for issue in self.issues:
            lines.append(f"  [{issue.severity.upper()}] {issue.key}: {issue.message}")
        return "\n".join(lines)


def _is_placeholder(value: str) -> bool:
    lower = value.lower()
    return any(hint in lower for hint in _PLACEHOLDER_HINTS)


def _looks_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(token in upper for token in _REQUIRED_NONEMPTY)


def audit_env(path: str, env: Dict[str, Optional[str]]) -> AuditResult:
    """Audit a parsed env dict and return an AuditResult."""
    result = AuditResult(path=path)

    for key, value in env.items():
        if _looks_sensitive(key):
            if value is None or value.strip() == "":
                result.issues.append(
                    AuditIssue(key=key, message="sensitive key has empty value", severity="error")
                )
            elif _is_placeholder(value):
                result.issues.append(
                    AuditIssue(key=key, message=f"value looks like a placeholder: {value!r}", severity="warning")
                )

        if value and len(value) > 0 and value == value.upper() and len(value) >= 32 and " " not in value:
            # Looks like a raw secret exposed as an uppercase string — informational only
            pass  # intentionally not flagged; high false-positive rate

    return result
