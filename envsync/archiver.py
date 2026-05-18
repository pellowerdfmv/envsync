"""Archive and restore .env snapshots to/from compressed bundles."""
from __future__ import annotations

import gzip
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsync.parser import parse_env_file


@dataclass
class ArchiveEntry:
    path: str
    env: Dict[str, Optional[str]]
    captured_at: float


@dataclass
class ArchiveResult:
    entries: List[ArchiveEntry] = field(default_factory=list)
    archive_path: Optional[str] = None

    def __len__(self) -> int:
        return len(self.entries)

    def has_entries(self) -> bool:
        return bool(self.entries)

    def summary(self) -> str:
        n = len(self.entries)
        dest = self.archive_path or "<memory>"
        return f"Archived {n} file(s) -> {dest}"


def archive_envs(paths: List[Path], dest: Path) -> ArchiveResult:
    """Read each env file and write a compressed JSON bundle to *dest*."""
    entries: List[ArchiveEntry] = []
    for p in paths:
        env = parse_env_file(p)
        entries.append(ArchiveEntry(path=str(p), env=env, captured_at=time.time()))

    payload = [
        {"path": e.path, "env": e.env, "captured_at": e.captured_at}
        for e in entries
    ]
    dest.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, "wt", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    return ArchiveResult(entries=entries, archive_path=str(dest))


def restore_archive(archive: Path) -> List[ArchiveEntry]:
    """Load an archive bundle and return its entries (does not write files)."""
    with gzip.open(archive, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return [
        ArchiveEntry(path=item["path"], env=item["env"], captured_at=item["captured_at"])
        for item in payload
    ]
