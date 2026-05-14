"""Tests for envsync.extractor."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envsync.extractor import ExtractResult, extract_env, extract_env_file


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content))
    return path


@pytest.fixture()
def tmp_env(tmp_path: Path) -> Path:
    return _write(
        tmp_path / ".env",
        """
        DB_HOST=localhost
        DB_PORT=5432
        APP_KEY=secret
        EMPTY_VAL=
        """,
    )


# ---------------------------------------------------------------------------
# extract_env (dict-based)
# ---------------------------------------------------------------------------

def test_requested_keys_present_in_extracted() -> None:
    env = {"A": "1", "B": "2", "C": "3"}
    result = extract_env(env, ["A", "C"])
    assert "A" in result.extracted
    assert "C" in result.extracted


def test_unrequested_keys_absent() -> None:
    env = {"A": "1", "B": "2"}
    result = extract_env(env, ["A"])
    assert "B" not in result.extracted


def test_missing_key_recorded() -> None:
    env = {"A": "1"}
    result = extract_env(env, ["A", "MISSING"])
    assert "MISSING" in result.missing


def test_missing_key_not_in_extracted() -> None:
    env = {"A": "1"}
    result = extract_env(env, ["MISSING"])
    assert "MISSING" not in result.extracted


def test_strict_raises_on_missing_key() -> None:
    env = {"A": "1"}
    with pytest.raises(KeyError, match="MISSING"):
        extract_env(env, ["MISSING"], strict=True)


def test_none_value_preserved() -> None:
    env = {"A": None}
    result = extract_env(env, ["A"])
    assert result.extracted["A"] is None


def test_len_equals_extracted_count() -> None:
    env = {"A": "1", "B": "2", "C": "3"}
    result = extract_env(env, ["A", "B"])
    assert len(result) == 2


def test_has_missing_false_when_all_found() -> None:
    env = {"A": "1"}
    result = extract_env(env, ["A"])
    assert not result.has_missing()


def test_has_missing_true_when_absent() -> None:
    result = extract_env({}, ["X"])
    assert result.has_missing()


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_contains_extracted_count() -> None:
    env = {"A": "1", "B": "2"}
    result = extract_env(env, ["A", "B"])
    assert "2" in result.summary()


def test_summary_contains_missing_keys() -> None:
    result = extract_env({"A": "1"}, ["A", "GONE"])
    assert "GONE" in result.summary()


def test_summary_contains_source_path(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    result = ExtractResult(extracted={}, missing=[], source_path=p)
    assert str(p) in result.summary()


# ---------------------------------------------------------------------------
# extract_env_file
# ---------------------------------------------------------------------------

def test_extract_env_file_reads_keys(tmp_env: Path) -> None:
    result = extract_env_file(tmp_env, ["DB_HOST", "DB_PORT"])
    assert result.extracted["DB_HOST"] == "localhost"
    assert result.extracted["DB_PORT"] == "5432"


def test_extract_env_file_records_source_path(tmp_env: Path) -> None:
    result = extract_env_file(tmp_env, ["DB_HOST"])
    assert result.source_path == tmp_env
