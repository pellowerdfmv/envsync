"""Tests for envsync.deduplicator."""
from __future__ import annotations

from pathlib import Path

import pytest

from envsync.deduplicator import DeduplicateResult, deduplicate_env


@pytest.fixture
def tmp_env(tmp_path: Path):
    """Return a helper that writes content to a temp .env file."""
    env_file = tmp_path / ".env"

    def _write(content: str) -> Path:
        env_file.write_text(content)
        return env_file

    return _write


def test_no_duplicates_has_no_issues(tmp_env):
    path = tmp_env("FOO=bar\nBAZ=qux\n")
    result = deduplicate_env(path)
    assert not result.has_duplicates()
    assert len(result) == 0


def test_duplicate_key_detected(tmp_env):
    path = tmp_env("FOO=first\nFOO=second\n")
    result = deduplicate_env(path)
    assert result.has_duplicates()
    assert "FOO" in result.duplicates


def test_duplicate_records_all_values(tmp_env):
    path = tmp_env("KEY=alpha\nKEY=beta\nKEY=gamma\n")
    result = deduplicate_env(path)
    assert result.duplicates["KEY"] == ["alpha", "beta", "gamma"]


def test_last_wins_strategy_keeps_final_value(tmp_env):
    path = tmp_env("PORT=3000\nPORT=4000\n")
    result = deduplicate_env(path, strategy="last")
    assert result.deduped["PORT"] == "4000"


def test_first_wins_strategy_keeps_first_value(tmp_env):
    path = tmp_env("PORT=3000\nPORT=4000\n")
    result = deduplicate_env(path, strategy="first")
    assert result.deduped["PORT"] == "3000"


def test_unrelated_keys_preserved(tmp_env):
    path = tmp_env("FOO=1\nBAR=2\nFOO=3\n")
    result = deduplicate_env(path, strategy="last")
    assert result.deduped["BAR"] == "2"


def test_len_counts_duplicate_keys(tmp_env):
    path = tmp_env("A=1\nA=2\nB=x\nB=y\nC=z\n")
    result = deduplicate_env(path)
    assert len(result) == 2


def test_summary_no_duplicates(tmp_env):
    path = tmp_env("X=1\nY=2\n")
    result = deduplicate_env(path)
    assert "no duplicate" in result.summary()


def test_summary_lists_duplicate_keys(tmp_env):
    path = tmp_env("SECRET=old\nSECRET=new\n")
    result = deduplicate_env(path)
    summary = result.summary()
    assert "SECRET" in summary
    assert "1 duplicate" in summary


def test_invalid_strategy_raises(tmp_env):
    path = tmp_env("A=1\n")
    with pytest.raises(ValueError, match="Unknown strategy"):
        deduplicate_env(path, strategy="random")


def test_comments_and_blank_lines_ignored(tmp_env):
    content = "# comment\n\nFOO=bar\nFOO=baz\n"
    path = tmp_env(content)
    result = deduplicate_env(path)
    assert "FOO" in result.duplicates
    assert len(result.duplicates) == 1
