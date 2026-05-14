"""Tests for envsync.scorer."""
from __future__ import annotations

from pathlib import Path

import pytest

from envsync.scorer import ScoreResult, score_env


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p

    return _write


def test_returns_score_result(tmp_env):
    p = tmp_env("API_KEY=abc123\nDB_HOST=localhost\n")
    result = score_env(p)
    assert isinstance(result, ScoreResult)


def test_perfect_env_scores_one(tmp_env):
    p = tmp_env("API_KEY=abc123\nDB_HOST=localhost\nSECRET=xyz\n")
    result = score_env(p)
    assert result.score == pytest.approx(1.0)


def test_empty_file_scores_zero(tmp_env):
    p = tmp_env("")
    result = score_env(p)
    assert result.score == pytest.approx(0.0)
    assert result.total_keys == 0


def test_unset_keys_reduce_score(tmp_env):
    p = tmp_env("API_KEY=\nDB_HOST=localhost\n")
    result = score_env(p)
    assert result.score < 1.0
    assert any("unset" in pen for pen in result.penalties)


def test_lowercase_key_reduces_score(tmp_env):
    p = tmp_env("api_key=abc\nDB_HOST=localhost\n")
    result = score_env(p)
    assert result.score < 1.0
    assert any("UPPER_SNAKE" in pen for pen in result.penalties)


def test_placeholder_value_reduces_score(tmp_env):
    p = tmp_env("API_KEY=changeme\nDB_HOST=localhost\n")
    result = score_env(p)
    assert result.score < 1.0
    assert any("placeholder" in pen for pen in result.penalties)


def test_breakdown_keys_present(tmp_env):
    p = tmp_env("API_KEY=real_value\n")
    result = score_env(p)
    assert set(result.breakdown) == {"fill_rate", "naming", "placeholder", "unique"}


def test_breakdown_sums_to_score(tmp_env):
    p = tmp_env("API_KEY=abc\nDB_URL=postgres://localhost/db\n")
    result = score_env(p)
    assert sum(result.breakdown.values()) == pytest.approx(result.score, abs=1e-4)


def test_len_equals_total_keys(tmp_env):
    p = tmp_env("A=1\nB=2\nC=3\n")
    result = score_env(p)
    assert len(result) == 3


def test_summary_contains_score(tmp_env):
    p = tmp_env("API_KEY=value\n")
    result = score_env(p)
    assert "Score:" in result.summary()


def test_summary_contains_path(tmp_env):
    p = tmp_env("API_KEY=value\n")
    result = score_env(p)
    assert str(p) in result.summary()


def test_path_stored_on_result(tmp_env):
    p = tmp_env("X=1\n")
    result = score_env(p)
    assert result.path == p


def test_none_value_counted_as_unset(tmp_env):
    """A key with no value (parsed as None) should be treated as unset."""
    p = tmp_env("MISSING_KEY\nSET_KEY=hello\n")
    result = score_env(p)
    assert result.score < 1.0
