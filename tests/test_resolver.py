"""Tests for envsync.resolver."""
from pathlib import Path

import pytest

from envsync.resolver import (
    ResolveResult,
    has_overrides,
    resolve_envs,
    summary,
)


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a helper that writes a .env file and returns its path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


def test_resolve_single_file(tmp_env):
    p = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    result = resolve_envs([p])
    assert result.resolved == {"FOO": "bar", "BAZ": "qux"}


def test_last_file_wins_by_default(tmp_env):
    p1 = tmp_env("base.env", "FOO=base\nSHARED=base\n")
    p2 = tmp_env("override.env", "SHARED=override\nBAR=new\n")
    result = resolve_envs([p1, p2])
    assert result.resolved["SHARED"] == "override"
    assert result.resolved["FOO"] == "base"
    assert result.resolved["BAR"] == "new"


def test_first_wins_with_reverse_priority(tmp_env):
    p1 = tmp_env("base.env", "SHARED=first\n")
    p2 = tmp_env("override.env", "SHARED=second\n")
    result = resolve_envs([p1, p2], reverse_priority=True)
    assert result.resolved["SHARED"] == "first"


def test_sources_tracked(tmp_env):
    p1 = tmp_env("a.env", "FOO=1\n")
    p2 = tmp_env("b.env", "BAR=2\n")
    result = resolve_envs([p1, p2])
    assert result.sources["FOO"] == str(p1)
    assert result.sources["BAR"] == str(p2)


def test_overrides_recorded(tmp_env):
    p1 = tmp_env("a.env", "KEY=old\n")
    p2 = tmp_env("b.env", "KEY=new\n")
    result = resolve_envs([p1, p2])
    assert len(result.overrides) == 1
    key, old_src, new_src = result.overrides[0]
    assert key == "KEY"
    assert old_src == str(p1)
    assert new_src == str(p2)


def test_no_overrides_for_disjoint_files(tmp_env):
    p1 = tmp_env("a.env", "A=1\n")
    p2 = tmp_env("b.env", "B=2\n")
    result = resolve_envs([p1, p2])
    assert not has_overrides(result)


def test_has_overrides_true(tmp_env):
    p1 = tmp_env("a.env", "X=1\n")
    p2 = tmp_env("b.env", "X=2\n")
    result = resolve_envs([p1, p2])
    assert has_overrides(result)


def test_summary_contains_key_count(tmp_env):
    p = tmp_env("a.env", "A=1\nB=2\n")
    result = resolve_envs([p])
    s = summary(result)
    assert "2" in s


def test_summary_mentions_overrides(tmp_env):
    p1 = tmp_env("a.env", "KEY=old\n")
    p2 = tmp_env("b.env", "KEY=new\n")
    result = resolve_envs([p1, p2])
    s = summary(result)
    assert "overridden" in s
    assert "KEY" in s


def test_empty_paths_returns_empty_result():
    result = resolve_envs([])
    assert result.resolved == {}
    assert result.sources == {}
    assert result.overrides == []


def test_none_value_resolved(tmp_env):
    p = tmp_env("a.env", "EMPTY=\n")
    result = resolve_envs([p])
    assert result.resolved.get("EMPTY") is None
