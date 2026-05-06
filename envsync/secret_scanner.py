"""Scan a parsed env mapping for values that look like exposed secrets.

Heuristics
----------
- High-entropy strings (Shannon entropy > threshold) are flagged.
- Known placeholder patterns ("changeme", "todo", "example", …) are skipped.
- Keys with None / empty values are skipped.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_PLACEHOLDERS = frozenset({
    "changeme", "change_me", "todo", "fixme", "example",
    "your_secret_here", "insert_here", "replace_me", "xxxx",
    "1234", "password", "secret", "test", "dummy",
})

_DEFAULT_ENTROPY_THRESHOLD = 3.5
_DEFAULT_MIN_LENGTH = 8


def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    freq = {ch: value.count(ch) / len(value) for ch in set(value)}
    return -sum(p * math.log2(p) for p in freq.values())


@dataclass
class SecretFinding:
    key: str
    value: str
    entropy: float
    reason: str


@dataclass
class ScanResult:
    findings: List[SecretFinding] = field(default_factory=list)

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    def summary(self) -> str:
        if not self.findings:
            return "No exposed secrets detected."
        lines = [f"Found {len(self.findings)} potential secret(s):"]
        for f in self.findings:
            lines.append(f"  {f.key}: {f.reason} (entropy={f.entropy:.2f})")
        return "\n".join(lines)


def scan_env(
    env: Dict[str, Optional[str]],
    entropy_threshold: float = _DEFAULT_ENTROPY_THRESHOLD,
    min_length: int = _DEFAULT_MIN_LENGTH,
) -> ScanResult:
    """Scan *env* for values that appear to be real secrets."""
    result = ScanResult()
    for key, value in env.items():
        if not value:
            continue
        if value.lower() in _PLACEHOLDERS:
            continue
        if len(value) < min_length:
            continue
        entropy = _shannon_entropy(value)
        if entropy >= entropy_threshold:
            result.findings.append(
                SecretFinding(
                    key=key,
                    value=value,
                    entropy=entropy,
                    reason=f"high-entropy value (>{entropy_threshold})",
                )
            )
    return result
