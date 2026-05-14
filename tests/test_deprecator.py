"""Tests for envsync.deprecator."""
from __future__ import annotations

from pathlib import Path

import pytest

from envsync.deprecator import DeprecateResult, deprecate_env, deprecate_file


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _env(**kwargs):
    return {k: v for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# deprecate_env
# ---------------------------------------------------------------------------

def test_present_key_detected():
    result = deprecate_env(_env(OLD_KEY="val"), {"OLD_KEY": "use NEW_KEY"})
    assert "OLD_KEY" in result.present


def test_absent_key_recorded():
    result = deprecate_env(_env(NEW_KEY="val"), {"OLD_KEY": "use NEW_KEY"})
    assert "OLD_KEY" in result.absent


def test_has_deprecated_true_when_found():
    result = deprecate_env(_env(OLD_KEY="v"), {"OLD_KEY": "gone"})
    assert result.has_deprecated() is True


def test_has_deprecated_false_when_not_found():
    result = deprecate_env(_env(OTHER="v"), {"OLD_KEY": "gone"})
    assert result.has_deprecated() is False


def test_env_unchanged_by_default():
    env = _env(OLD_KEY="v", KEEP="x")
    result = deprecate_env(env, {"OLD_KEY": "gone"})
    assert "OLD_KEY" in result.env
    assert result.env["KEEP"] == "x"


def test_remove_flag_strips_deprecated_key():
    env = _env(OLD_KEY="v", KEEP="x")
    result = deprecate_env(env, {"OLD_KEY": "gone"}, remove=True)
    assert "OLD_KEY" not in result.env
    assert result.env["KEEP"] == "x"


def test_remove_does_not_affect_absent_keys():
    env = _env(KEEP="x")
    result = deprecate_env(env, {"OLD_KEY": "gone"}, remove=True)
    assert result.env == {"KEEP": "x"}


def test_len_reflects_result_env():
    env = _env(A="1", B="2", C="3")
    result = deprecate_env(env, {"A": "old"}, remove=True)
    assert len(result) == 2


def test_source_path_stored():
    p = Path("/some/.env")
    result = deprecate_env(_env(X="1"), {}, source_path=p)
    assert result.source_path == p


def test_summary_contains_counts():
    result = deprecate_env(_env(OLD="v", ALSO_OLD="v"), {"OLD": "x", "ALSO_OLD": "y", "GONE": "z"})
    s = result.summary()
    assert "2/3" in s


def test_present_and_absent_are_sorted():
    env = _env(B_OLD="v", A_OLD="v")
    result = deprecate_env(env, {"B_OLD": "", "A_OLD": "", "C_OLD": ""})
    assert result.present == ["A_OLD", "B_OLD"]
    assert result.absent == ["C_OLD"]


# ---------------------------------------------------------------------------
# deprecate_file
# ---------------------------------------------------------------------------

def test_deprecate_file_reads_path(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("OLD_DB_URL=postgres://localhost/old\nKEEP=yes\n")
    result = deprecate_file(env_file, {"OLD_DB_URL": "use DATABASE_URL"})
    assert result.has_deprecated() is True
    assert result.source_path == env_file


def test_deprecate_file_remove_strips_key(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("OLD=1\nNEW=2\n")
    result = deprecate_file(env_file, {"OLD": "gone"}, remove=True)
    assert "OLD" not in result.env
    assert result.env.get("NEW") == "2"
