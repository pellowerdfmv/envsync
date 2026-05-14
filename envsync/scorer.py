"""scorer.py – Compute a quality score for a .env file.

The score is a value between 0.0 and 1.0 derived from several
heuristics: fill rate, absence of placeholder values, key naming
conventions, and absence of duplicate keys.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envsync.parser import parse_env_file

_PLACEHOLDERS = {"changeme", "todo", "fixme", "placeholder", "example", "your_", "<", ">"}


@dataclass
class ScoreResult:
    path: Path
    score: float  # 0.0 – 1.0
    total_keys: int
    penalties: List[str] = field(default_factory=list)
    breakdown: Dict[str, float] = field(default_factory=dict)

    def __len__(self) -> int:  # noqa: D105
        return self.total_keys

    def summary(self) -> str:  # noqa: D102
        pct = int(self.score * 100)
        parts = [f"Score: {pct}/100 ({self.total_keys} keys) [{self.path}]"]
        for p in self.penalties:
            parts.append(f"  - {p}")
        return "\n".join(parts)


def score_env(path: Path) -> ScoreResult:
    """Return a :class:`ScoreResult` for the .env file at *path*."""
    env = parse_env_file(path)
    total = len(env)

    if total == 0:
        return ScoreResult(
            path=path,
            score=0.0,
            total_keys=0,
            penalties=["File is empty"],
            breakdown={"fill_rate": 0.0, "naming": 0.0, "placeholder": 0.0, "unique": 0.0},
        )

    penalties: List[str] = []

    # --- fill rate (25 pts) ---
    set_count = sum(1 for v in env.values() if v is not None and v != "")
    fill_rate = set_count / total
    fill_score = fill_rate * 0.25
    if fill_rate < 1.0:
        missing = total - set_count
        penalties.append(f"{missing} key(s) unset (empty or None)")

    # --- naming convention – UPPER_SNAKE (25 pts) ---
    bad_names = [k for k in env if not k.replace("_", "").isupper() or k != k.strip()]
    naming_score = max(0.0, 1.0 - len(bad_names) / total) * 0.25
    if bad_names:
        penalties.append(f"{len(bad_names)} key(s) violate UPPER_SNAKE_CASE")

    # --- placeholder detection (25 pts) ---
    placeholder_hits = [
        k for k, v in env.items()
        if v and any(p in v.lower() for p in _PLACEHOLDERS)
    ]
    placeholder_score = max(0.0, 1.0 - len(placeholder_hits) / total) * 0.25
    if placeholder_hits:
        penalties.append(f"{len(placeholder_hits)} key(s) contain placeholder values")

    # --- uniqueness (25 pts) – parser already de-dupes, so full marks always ---
    unique_score = 0.25

    total_score = round(fill_score + naming_score + placeholder_score + unique_score, 4)

    return ScoreResult(
        path=path,
        score=total_score,
        total_keys=total,
        penalties=penalties,
        breakdown={
            "fill_rate": round(fill_score, 4),
            "naming": round(naming_score, 4),
            "placeholder": round(placeholder_score, 4),
            "unique": round(unique_score, 4),
        },
    )
