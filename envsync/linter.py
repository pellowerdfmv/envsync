"""Lint .env files for style and convention issues."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_LEADING_SPACE = re.compile(r'^\s+')
_TRAILING_SPACE = re.compile(r'\s+$')


@dataclass
class LintIssue:
    line: int
    key: Optional[str]
    code: str
    message: str
    severity: str  # 'error' | 'warning'


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)

    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == 'error']

    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == 'warning']

    def summary(self) -> str:
        e, w = len(self.errors()), len(self.warnings())
        return f"{self.path}: {e} error(s), {w} warning(s)"


def lint_env(path: str, parsed: Dict[str, Optional[str]]) -> LintResult:
    """Lint a parsed env file and return a LintResult."""
    result = LintResult(path=path)

    with open(path, encoding='utf-8') as fh:
        lines = fh.readlines()

    seen_keys: Dict[str, int] = {}

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.rstrip('\n')

        if not stripped or stripped.lstrip().startswith('#'):
            continue

        if _LEADING_SPACE.match(stripped):
            result.issues.append(LintIssue(
                line=lineno, key=None, code='E001',
                message='Line has unexpected leading whitespace.',
                severity='error',
            ))

        if '=' not in stripped:
            continue

        key, _, value = stripped.partition('=')
        key = key.strip()

        if _TRAILING_SPACE.search(key):
            result.issues.append(LintIssue(
                line=lineno, key=key, code='W001',
                message=f"Key '{key}' has trailing whitespace.",
                severity='warning',
            ))
            key = key.rstrip()

        if not _UPPER_SNAKE.match(key):
            result.issues.append(LintIssue(
                line=lineno, key=key, code='W002',
                message=f"Key '{key}' should be UPPER_SNAKE_CASE.",
                severity='warning',
            ))

        if key in seen_keys:
            result.issues.append(LintIssue(
                line=lineno, key=key, code='E002',
                message=f"Duplicate key '{key}' (first seen on line {seen_keys[key]}).",
                severity='error',
            ))
        else:
            seen_keys[key] = lineno

        if _TRAILING_SPACE.search(value):
            result.issues.append(LintIssue(
                line=lineno, key=key, code='W003',
                message=f"Value for '{key}' has trailing whitespace.",
                severity='warning',
            ))

    return result
