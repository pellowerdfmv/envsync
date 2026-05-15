"""Tests for envsync.mapper."""
from __future__ import annotations

from pathlib import Path

import pytest

from envsync.mapper import MapResult, map_env, map_env_file


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a helper that writes an .env file and returns its path."""
    def _write(text: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(text)
        return p
    return _write


SIMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_DEBUG": "true"}


# ---------------------------------------------------------------------------
# map_env — basic behaviour
# ---------------------------------------------------------------------------

def test_returns_map_result():
    result = map_env(SIMPLE, {})
    assert isinstance(result, MapResult)


def test_empty_mapping_leaves_env_unchanged():
    result = map_env(SIMPLE, {})
    assert result.mapped == SIMPLE


def test_key_is_renamed():
    result = map_env(SIMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.mapped
    assert "DB_HOST" not in result.mapped


def test_renamed_value_preserved():
    result = map_env(SIMPLE, {"DB_PORT": "DATABASE_PORT"})
    assert result.mapped["DATABASE_PORT"] == "5432"


def test_unrelated_keys_untouched():
    result = map_env(SIMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert result.mapped["APP_DEBUG"] == "true"
    assert result.mapped["DB_PORT"] == "5432"


def test_applied_records_used_mapping():
    result = map_env(SIMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert result.applied == {"DB_HOST": "DATABASE_HOST"}


def test_skipped_records_absent_source_key():
    result = map_env(SIMPLE, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert result.skipped["MISSING_KEY"] == "NEW_KEY"


def test_skipped_key_not_added_to_mapped():
    result = map_env(SIMPLE, {"MISSING_KEY": "NEW_KEY"})
    assert "NEW_KEY" not in result.mapped
    assert "MISSING_KEY" not in result.mapped


def test_multiple_renames_applied():
    result = map_env(SIMPLE, {"DB_HOST": "HOST", "DB_PORT": "PORT"})
    assert "HOST" in result.mapped
    assert "PORT" in result.mapped
    assert len(result.applied) == 2


def test_none_value_preserved_after_rename():
    env = {"SECRET": None}
    result = map_env(env, {"SECRET": "APP_SECRET"})
    assert result.mapped["APP_SECRET"] is None


# ---------------------------------------------------------------------------
# has_remaps / summary / len
# ---------------------------------------------------------------------------

def test_has_remaps_true_when_applied():
    result = map_env(SIMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert result.has_remaps() is True


def test_has_remaps_false_when_nothing_applied():
    result = map_env(SIMPLE, {"MISSING": "X"})
    assert result.has_remaps() is False


def test_len_equals_key_count():
    result = map_env(SIMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert len(result) == len(SIMPLE)


def test_summary_contains_remapped_count():
    result = map_env(SIMPLE, {"DB_HOST": "DATABASE_HOST"})
    assert "1 remapped" in result.summary()


def test_summary_contains_skipped_count():
    result = map_env(SIMPLE, {"MISSING": "X"})
    assert "skipped" in result.summary()


def test_summary_contains_source_path(tmp_path: Path):
    p = tmp_path / ".env"
    result = map_env(SIMPLE, {}, source_path=p)
    assert str(p) in result.summary()


# ---------------------------------------------------------------------------
# map_env_file
# ---------------------------------------------------------------------------

def test_map_env_file_renames_key(tmp_env):
    p = tmp_env("DB_HOST=localhost\nDB_PORT=5432\n")
    result = map_env_file(p, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.mapped
    assert "DB_HOST" not in result.mapped


def test_map_env_file_stores_source_path(tmp_env):
    p = tmp_env("KEY=value\n")
    result = map_env_file(p, {})
    assert result.source_path == p
