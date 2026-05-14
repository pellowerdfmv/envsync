"""Tests for envsync.promoter."""
from pathlib import Path

import pytest

from envsync.promoter import promote_env, PromoteResult


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


# ---------------------------------------------------------------------------
# Basic promotion
# ---------------------------------------------------------------------------

def test_promote_result_type(tmp_env):
    src = tmp_env("src.env", "FOO=bar\n")
    tgt = tmp_env("tgt.env", "BAZ=qux\n")
    result = promote_env(src, tgt)
    assert isinstance(result, PromoteResult)


def test_new_key_is_promoted(tmp_env):
    src = tmp_env("src.env", "FOO=bar\n")
    tgt = tmp_env("tgt.env", "BAZ=qux\n")
    result = promote_env(src, tgt)
    assert "FOO" in result.promoted


def test_promoted_value_in_merged(tmp_env):
    src = tmp_env("src.env", "FOO=bar\n")
    tgt = tmp_env("tgt.env", "BAZ=qux\n")
    result = promote_env(src, tgt)
    assert result.merged["FOO"] == "bar"


def test_existing_key_skipped_by_default(tmp_env):
    src = tmp_env("src.env", "FOO=new_val\n")
    tgt = tmp_env("tgt.env", "FOO=old_val\n")
    result = promote_env(src, tgt)
    assert "FOO" in result.skipped
    assert result.merged["FOO"] == "old_val"


def test_existing_key_overwritten_when_flag_set(tmp_env):
    src = tmp_env("src.env", "FOO=new_val\n")
    tgt = tmp_env("tgt.env", "FOO=old_val\n")
    result = promote_env(src, tgt, overwrite=True)
    assert "FOO" in result.promoted
    assert result.merged["FOO"] == "new_val"


def test_target_only_keys_preserved(tmp_env):
    src = tmp_env("src.env", "FOO=bar\n")
    tgt = tmp_env("tgt.env", "BAZ=qux\n")
    result = promote_env(src, tgt)
    assert "BAZ" in result.merged
    assert result.merged["BAZ"] == "qux"


# ---------------------------------------------------------------------------
# Key allowlist
# ---------------------------------------------------------------------------

def test_keys_allowlist_limits_promotion(tmp_env):
    src = tmp_env("src.env", "FOO=1\nBAR=2\nBAZ=3\n")
    tgt = tmp_env("tgt.env", "")
    result = promote_env(src, tgt, keys=["FOO", "BAZ"])
    assert "FOO" in result.promoted
    assert "BAZ" in result.promoted
    assert "BAR" not in result.promoted
    assert "BAR" not in result.merged


def test_keys_allowlist_with_missing_key_ignored(tmp_env):
    src = tmp_env("src.env", "FOO=1\n")
    tgt = tmp_env("tgt.env", "")
    result = promote_env(src, tgt, keys=["FOO", "NONEXISTENT"])
    assert "FOO" in result.promoted
    assert "NONEXISTENT" not in result.merged


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def test_len_equals_promoted_count(tmp_env):
    src = tmp_env("src.env", "A=1\nB=2\n")
    tgt = tmp_env("tgt.env", "")
    result = promote_env(src, tgt)
    assert len(result) == 2


def test_has_promotions_true(tmp_env):
    src = tmp_env("src.env", "A=1\n")
    tgt = tmp_env("tgt.env", "")
    result = promote_env(src, tgt)
    assert result.has_promotions() is True


def test_has_promotions_false_when_all_skipped(tmp_env):
    src = tmp_env("src.env", "A=1\n")
    tgt = tmp_env("tgt.env", "A=existing\n")
    result = promote_env(src, tgt)
    assert result.has_promotions() is False


def test_summary_contains_source_and_target(tmp_env):
    src = tmp_env("src.env", "A=1\n")
    tgt = tmp_env("tgt.env", "")
    result = promote_env(src, tgt)
    s = result.summary()
    assert "src.env" in s
    assert "tgt.env" in s


def test_summary_contains_counts(tmp_env):
    src = tmp_env("src.env", "A=1\nB=2\n")
    tgt = tmp_env("tgt.env", "B=old\n")
    result = promote_env(src, tgt)
    s = result.summary()
    assert "1" in s  # 1 promoted
    assert "skipped" in s
