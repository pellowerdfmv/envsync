"""Tests for envsync.snapshot."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from envsync.snapshot import (
    Snapshot,
    SnapshotDiff,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


def test_take_snapshot_captures_keys(tmp_env):
    p = tmp_env(".env", "FOO=bar\nBAZ=qux\n")
    snap = take_snapshot(p)
    assert "FOO" in snap.keys
    assert "BAZ" in snap.keys


def test_take_snapshot_records_path(tmp_env):
    p = tmp_env(".env", "X=1\n")
    snap = take_snapshot(p)
    assert snap.path == str(p)


def test_take_snapshot_timestamp_is_recent(tmp_env):
    p = tmp_env(".env", "X=1\n")
    before = time.time()
    snap = take_snapshot(p)
    after = time.time()
    assert before <= snap.timestamp <= after


def test_save_and_load_round_trip(tmp_env, tmp_path):
    p = tmp_env(".env", "KEY=value\n")
    snap = take_snapshot(p)
    dest = tmp_path / "snap.json"
    save_snapshot(snap, dest)
    loaded = load_snapshot(dest)
    assert loaded.path == snap.path
    assert loaded.keys == snap.keys
    assert loaded.env == snap.env


def test_saved_snapshot_is_valid_json(tmp_env, tmp_path):
    p = tmp_env(".env", "A=1\n")
    snap = take_snapshot(p)
    dest = tmp_path / "snap.json"
    save_snapshot(snap, dest)
    data = json.loads(dest.read_text())
    assert "keys" in data and "env" in data


def test_diff_snapshots_detects_added():
    before = Snapshot(path=".env", timestamp=0.0, keys=["A"], env={"A": "1"})
    after = Snapshot(path=".env", timestamp=1.0, keys=["A", "B"], env={"A": "1", "B": "2"})
    diff = diff_snapshots(before, after)
    assert "B" in diff.added
    assert diff.removed == []


def test_diff_snapshots_detects_removed():
    before = Snapshot(path=".env", timestamp=0.0, keys=["A", "B"], env={"A": "1", "B": "2"})
    after = Snapshot(path=".env", timestamp=1.0, keys=["A"], env={"A": "1"})
    diff = diff_snapshots(before, after)
    assert "B" in diff.removed
    assert diff.added == []


def test_diff_snapshots_detects_changed():
    before = Snapshot(path=".env", timestamp=0.0, keys=["A"], env={"A": "old"})
    after = Snapshot(path=".env", timestamp=1.0, keys=["A"], env={"A": "new"})
    diff = diff_snapshots(before, after)
    assert "A" in diff.changed


def test_diff_no_changes_when_identical():
    snap = Snapshot(path=".env", timestamp=0.0, keys=["A"], env={"A": "1"})
    diff = diff_snapshots(snap, snap)
    assert not diff.has_changes()


def test_summary_no_changes():
    diff = SnapshotDiff()
    assert diff.summary() == "no changes"


def test_summary_with_changes():
    diff = SnapshotDiff(added=["X"], removed=["Y"], changed=["Z"])
    assert "+1 added" in diff.summary()
    assert "-1 removed" in diff.summary()
    assert "~1 changed" in diff.summary()
