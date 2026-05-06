"""Tests for envsync.merger."""

from __future__ import annotations

import pytest

from envsync.merger import merge_envs


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str):
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_merge_two_disjoint_files(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "BAZ=3\n")
    result = merge_envs(a, b)
    assert result.merged == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert not result.has_conflicts()


def test_last_wins_strategy(tmp_env):
    a = tmp_env("a.env", "FOO=original\n")
    b = tmp_env("b.env", "FOO=override\n")
    result = merge_envs(a, b, strategy="last_wins")
    assert result.merged["FOO"] == "override"


def test_first_wins_strategy(tmp_env):
    a = tmp_env("a.env", "FOO=original\n")
    b = tmp_env("b.env", "FOO=override\n")
    result = merge_envs(a, b, strategy="first_wins")
    assert result.merged["FOO"] == "original"


def test_conflict_detected_when_values_differ(tmp_env):
    a = tmp_env("a.env", "SECRET=abc\n")
    b = tmp_env("b.env", "SECRET=xyz\n")
    result = merge_envs(a, b)
    assert result.has_conflicts()
    assert "SECRET" in result.conflicts
    sources = [src for src, _ in result.conflicts["SECRET"]]
    assert str(a) in sources
    assert str(b) in sources


def test_no_conflict_when_same_value(tmp_env):
    a = tmp_env("a.env", "PORT=8080\n")
    b = tmp_env("b.env", "PORT=8080\n")
    result = merge_envs(a, b)
    assert not result.has_conflicts()


def test_sources_recorded(tmp_env):
    a = tmp_env("a.env", "X=1\n")
    b = tmp_env("b.env", "Y=2\n")
    result = merge_envs(a, b)
    assert result.sources == [str(a), str(b)]


def test_invalid_strategy_raises(tmp_env):
    a = tmp_env("a.env", "X=1\n")
    with pytest.raises(ValueError, match="Unknown strategy"):
        merge_envs(a, strategy="random")


def test_summary_no_conflicts(tmp_env):
    a = tmp_env("a.env", "A=1\n")
    result = merge_envs(a)
    assert "No conflicts" in result.summary()


def test_summary_with_conflicts(tmp_env):
    a = tmp_env("a.env", "KEY=v1\n")
    b = tmp_env("b.env", "KEY=v2\n")
    result = merge_envs(a, b)
    assert "KEY" in result.summary()
    assert "Conflicts" in result.summary()


def test_none_value_no_false_conflict(tmp_env):
    a = tmp_env("a.env", "EMPTY=\n")
    b = tmp_env("b.env", "EMPTY=\n")
    result = merge_envs(a, b)
    assert not result.has_conflicts()
