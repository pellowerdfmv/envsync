"""Label env keys with arbitrary string tags for categorisation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .parser import parse_env_file


@dataclass
class LabelResult:
    """Result of labeling an env mapping."""

    labeled: Dict[str, List[str]] = field(default_factory=dict)  # key -> [label, ...]
    unlabeled: List[str] = field(default_factory=list)
    source_path: Optional[Path] = None

    def __len__(self) -> int:  # noqa: D105
        return len(self.labeled) + len(self.unlabeled)

    def has_labels(self) -> bool:
        """Return True when at least one key carries a label."""
        return bool(self.labeled)

    def keys_with_label(self, label: str) -> List[str]:
        """Return all keys that carry *label*."""
        return [k for k, labels in self.labeled.items() if label in labels]

    def summary(self) -> str:  # noqa: D102
        total = len(self)
        n_labeled = len(self.labeled)
        src = f" ({self.source_path})" if self.source_path else ""
        return (
            f"LabelResult{src}: {total} keys, "
            f"{n_labeled} labeled, {len(self.unlabeled)} unlabeled"
        )


def label_env(
    env: Dict[str, object],
    rules: Dict[str, List[str]],
    *,
    source_path: Optional[Path] = None,
) -> LabelResult:
    """Assign labels to *env* keys according to *rules*.

    *rules* maps a label name to the list of keys that should receive it.
    A key may receive multiple labels if it appears in several rule lists.
    Keys absent from all rules land in ``unlabeled``.
    """
    labeled: Dict[str, List[str]] = {}
    for label, keys in rules.items():
        for key in keys:
            if key in env:
                labeled.setdefault(key, []).append(label)

    unlabeled = [k for k in env if k not in labeled]
    return LabelResult(
        labeled=labeled,
        unlabeled=unlabeled,
        source_path=source_path,
    )


def label_env_file(
    path: Path,
    rules: Dict[str, List[str]],
) -> LabelResult:
    """Parse *path* and label its keys using *rules*."""
    env = parse_env_file(path)
    return label_env(env, rules, source_path=path)
