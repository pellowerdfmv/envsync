"""Tests for envsync.archiver."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envsync.archiver import ArchiveResult, archive_envs, restore_archive


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(name: str, text: str) -> Path:
        p = tmp_path / name
        p.write_text(text)
        return p
    return _write


def test_archive_returns_archive_result(tmp_env, tmp_path):
    f = tmp_env("a.env", "KEY=value\n")
    result = archive_envs([f], tmp_path / "out.env.gz")
    assert isinstance(result, ArchiveResult)


def test_archive_len_equals_file_count(tmp_env, tmp_path):
    f1 = tmp_env("a.env", "A=1\n")
    f2 = tmp_env("b.env", "B=2\n")
    result = archive_envs([f1, f2], tmp_path / "out.env.gz")
    assert len(result) == 2


def test_archive_has_entries_true(tmp_env, tmp_path):
    f = tmp_env("a.env", "X=1\n")
    result = archive_envs([f], tmp_path / "out.env.gz")
    assert result.has_entries()


def test_archive_file_created(tmp_env, tmp_path):
    f = tmp_env("a.env", "X=1\n")
    dest = tmp_path / "bundle.env.gz"
    archive_envs([f], dest)
    assert dest.exists()


def test_archive_path_stored_in_result(tmp_env, tmp_path):
    f = tmp_env("a.env", "X=1\n")
    dest = tmp_path / "bundle.env.gz"
    result = archive_envs([f], dest)
    assert result.archive_path == str(dest)


def test_summary_contains_file_count(tmp_env, tmp_path):
    f = tmp_env("a.env", "A=1\n")
    result = archive_envs([f], tmp_path / "out.env.gz")
    assert "1" in result.summary()


def test_restore_returns_entries(tmp_env, tmp_path):
    f = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    dest = tmp_path / "out.env.gz"
    archive_envs([f], dest)
    entries = restore_archive(dest)
    assert len(entries) == 1


def test_restore_env_keys_match(tmp_env, tmp_path):
    f = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    dest = tmp_path / "out.env.gz"
    archive_envs([f], dest)
    entries = restore_archive(dest)
    assert entries[0].env == {"FOO": "bar", "BAZ": "qux"}


def test_restore_captured_at_is_recent(tmp_env, tmp_path):
    f = tmp_env("a.env", "K=v\n")
    dest = tmp_path / "out.env.gz"
    before = time.time()
    archive_envs([f], dest)
    entries = restore_archive(dest)
    assert entries[0].captured_at >= before


def test_restore_path_recorded(tmp_env, tmp_path):
    f = tmp_env("myapp.env", "K=v\n")
    dest = tmp_path / "out.env.gz"
    archive_envs([f], dest)
    entries = restore_archive(dest)
    assert "myapp.env" in entries[0].path


def test_multiple_files_all_restored(tmp_env, tmp_path):
    f1 = tmp_env("a.env", "A=1\n")
    f2 = tmp_env("b.env", "B=2\n")
    dest = tmp_path / "out.env.gz"
    archive_envs([f1, f2], dest)
    entries = restore_archive(dest)
    assert len(entries) == 2
