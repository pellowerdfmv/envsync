"""Snapshot: capture and compare .env state at different points in time."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsync.parser import parse_env_file


@dataclass
class Snapshot:
    path: str
    timestamp: float
    keys: List[str]
    env: Dict[str, Optional[str]]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "timestamp": self.timestamp,
            "keys": self.keys,
            "env": {k: v for k, v in self.env.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            path=data["path"],
            timestamp=data["timestamp"],
            keys=data["keys"],
            env=data["env"],
        )


@dataclass
class SnapshotDiff:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        return ", ".join(parts) if parts else "no changes"


def take_snapshot(env_path: Path) -> Snapshot:
    """Parse *env_path* and return a Snapshot capturing the current state."""
    env = parse_env_file(env_path)
    return Snapshot(
        path=str(env_path),
        timestamp=time.time(),
        keys=list(env.keys()),
        env=env,
    )


def save_snapshot(snapshot: Snapshot, dest: Path) -> None:
    """Persist *snapshot* as JSON to *dest*."""
    dest.write_text(json.dumps(snapshot.to_dict(), indent=2))


def load_snapshot(src: Path) -> Snapshot:
    """Load a previously saved Snapshot from *src*."""
    data = json.loads(src.read_text())
    return Snapshot.from_dict(data)


def diff_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDiff:
    """Compare two snapshots and return what changed between them."""
    before_keys = set(before.keys)
    after_keys = set(after.keys)

    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    common = before_keys & after_keys
    changed = sorted(
        k for k in common if before.env.get(k) != after.env.get(k)
    )
    return SnapshotDiff(added=added, removed=removed, changed=changed)
