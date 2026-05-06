"""SnapshotStore: manage a directory of named .env snapshots."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from envsync.snapshot import Snapshot, load_snapshot, save_snapshot, take_snapshot

_SUFFIX = ".snap.json"


class SnapshotStore:
    """Persist and retrieve named snapshots under a single directory."""

    def __init__(self, store_dir: Path) -> None:
        self.store_dir = store_dir
        store_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _snap_path(self, name: str) -> Path:
        return self.store_dir / f"{name}{_SUFFIX}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def capture(self, name: str, env_path: Path) -> Snapshot:
        """Take a snapshot of *env_path* and save it under *name*."""
        snap = take_snapshot(env_path)
        save_snapshot(snap, self._snap_path(name))
        return snap

    def load(self, name: str) -> Snapshot:
        """Load the snapshot stored under *name*."""
        p = self._snap_path(name)
        if not p.exists():
            raise FileNotFoundError(f"No snapshot named '{name}' in {self.store_dir}")
        return load_snapshot(p)

    def delete(self, name: str) -> bool:
        """Remove the snapshot named *name*. Returns True if it existed."""
        p = self._snap_path(name)
        if p.exists():
            p.unlink()
            return True
        return False

    def list_snapshots(self) -> List[str]:
        """Return all snapshot names currently in the store."""
        return sorted(
            p.name[: -len(_SUFFIX)]
            for p in self.store_dir.glob(f"*{_SUFFIX}")
        )

    def exists(self, name: str) -> bool:
        return self._snap_path(name).exists()
