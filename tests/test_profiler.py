"""Tests for envsync.profiler."""
from __future__ import annotations

import os
import pytest

from envsync.profiler import profile_env, ProfileResult


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(p, text: str) -> str:
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_total_keys_counted(tmp_env):
    path = _write(tmp_env, "A=1\nB=2\nC=3\n")
    result = profile_env(path)
    assert result.total_keys == 3


def test_set_keys_counted(tmp_env):
    path = _write(tmp_env, "A=hello\nB=world\n")
    result = profile_env(path)
    assert result.set_keys == 2
    assert result.empty_keys == 0
    assert result.null_keys == 0


def test_empty_key_counted(tmp_env):
    path = _write(tmp_env, "A=\nB=value\n")
    result = profile_env(path)
    assert result.empty_keys == 1
    assert result.set_keys == 1


def test_null_key_counted(tmp_env):
    # parser returns None for bare keys with no '='
    path = _write(tmp_env, "BARE_KEY\nB=value\n")
    result = profile_env(path)
    assert result.null_keys == 1
    assert result.set_keys == 1


def test_fill_rate_all_set(tmp_env):
    path = _write(tmp_env, "A=1\nB=2\n")
    result = profile_env(path)
    assert result.fill_rate == pytest.approx(1.0)


def test_fill_rate_partial(tmp_env):
    path = _write(tmp_env, "A=1\nB=\n")
    result = profile_env(path)
    assert result.fill_rate == pytest.approx(0.5)


def test_fill_rate_empty_file(tmp_env):
    path = _write(tmp_env, "")
    result = profile_env(path)
    assert result.fill_rate == 0.0


def test_comment_lines_counted(tmp_env):
    path = _write(tmp_env, "# comment\nA=1\n# another\n")
    result = profile_env(path)
    assert result.comment_lines == 2


def test_blank_lines_counted(tmp_env):
    path = _write(tmp_env, "A=1\n\nB=2\n\n")
    result = profile_env(path)
    assert result.blank_lines == 2


def test_unset_keys_property(tmp_env):
    path = _write(tmp_env, "A=\nBARE\nC=ok\n")
    result = profile_env(path)
    assert result.unset_keys == result.empty_keys + result.null_keys


def test_summary_contains_path(tmp_env):
    path = _write(tmp_env, "A=1\n")
    result = profile_env(path)
    assert path in result.summary()


def test_key_lengths_recorded(tmp_env):
    path = _write(tmp_env, "SHORT=1\nA_LONGER_KEY=2\n")
    result = profile_env(path)
    assert result.key_lengths["SHORT"] == len("SHORT")
    assert result.key_lengths["A_LONGER_KEY"] == len("A_LONGER_KEY")
