"""Tests for envsync.snapshot_store."""
from __future__ import annotations

from pathlib import Path

import pytest

from envsync.snapshot_store import SnapshotStore


@pytest.fixture()
def store(tmp_path: Path) -> SnapshotStore:
    return SnapshotStore(tmp_path / "snaps")


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    return p


def test_capture_returns_snapshot(store, env_file):
    snap = store.capture("v1", env_file)
    assert "FOO" in snap.keys


def test_capture_persists_to_disk(store, env_file):
    store.capture("v1", env_file)
    assert store.exists("v1")


def test_load_restores_snapshot(store, env_file):
    store.capture("v1", env_file)
    snap = store.load("v1")
    assert snap.env.get("FOO") == "bar"


def test_load_unknown_raises(store):
    with pytest.raises(FileNotFoundError, match="no_such"):
        store.load("no_such")


def test_list_snapshots_empty_initially(store):
    assert store.list_snapshots() == []


def test_list_snapshots_after_capture(store, env_file):
    store.capture("alpha", env_file)
    store.capture("beta", env_file)
    names = store.list_snapshots()
    assert "alpha" in names
    assert "beta" in names


def test_list_snapshots_sorted(store, env_file):
    store.capture("z_snap", env_file)
    store.capture("a_snap", env_file)
    names = store.list_snapshots()
    assert names == sorted(names)


def test_delete_existing_snapshot(store, env_file):
    store.capture("v1", env_file)
    removed = store.delete("v1")
    assert removed is True
    assert not store.exists("v1")


def test_delete_nonexistent_returns_false(store):
    assert store.delete("ghost") is False


def test_store_dir_created_automatically(tmp_path):
    nested = tmp_path / "deep" / "nested" / "store"
    s = SnapshotStore(nested)
    assert nested.is_dir()


def test_exists_false_before_capture(store):
    assert not store.exists("missing")
