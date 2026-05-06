"""Tests for envsync.comparator."""

from __future__ import annotations

import os
import pytest

from envsync.comparator import compare_envs


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_all_keys_collected(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=1\nBAZ=3\n")
    result = compare_envs([a, b])
    assert result.all_keys == {"FOO", "BAR", "BAZ"}


def test_common_keys_identified(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=9\nBAR=2\n")
    result = compare_envs([a, b])
    assert result.common_keys == {"FOO", "BAR"}


def test_unique_keys_per_file(tmp_env):
    a = tmp_env("a.env", "ONLY_A=1\nSHARED=x\n")
    b = tmp_env("b.env", "ONLY_B=2\nSHARED=x\n")
    result = compare_envs([a, b])
    assert "ONLY_A" in result.unique_keys[a]
    assert "ONLY_B" in result.unique_keys[b]
    assert "SHARED" not in result.unique_keys[a]


def test_matrix_contains_values(tmp_env):
    a = tmp_env("a.env", "KEY=hello\n")
    b = tmp_env("b.env", "KEY=world\n")
    result = compare_envs([a, b])
    assert result.matrix["KEY"][a] == "hello"
    assert result.matrix["KEY"][b] == "world"


def test_keys_missing_in_file(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=1\n")
    result = compare_envs([a, b])
    missing = result.keys_missing_in(b)
    assert "BAR" in missing
    assert "FOO" not in missing


def test_value_conflicts_detected(tmp_env):
    a = tmp_env("a.env", "HOST=localhost\nPORT=5432\n")
    b = tmp_env("b.env", "HOST=prod.example.com\nPORT=5432\n")
    result = compare_envs([a, b])
    conflicts = result.value_conflicts()
    assert "HOST" in conflicts
    assert "PORT" not in conflicts


def test_no_conflicts_when_values_match(tmp_env):
    a = tmp_env("a.env", "KEY=same\n")
    b = tmp_env("b.env", "KEY=same\n")
    result = compare_envs([a, b])
    assert result.value_conflicts() == {}


def test_single_file_accepted(tmp_env):
    a = tmp_env("a.env", "SOLO=1\n")
    result = compare_envs([a])
    assert "SOLO" in result.all_keys


def test_empty_paths_raises(tmp_env):
    with pytest.raises(ValueError, match="At least one path"):
        compare_envs([])


def test_three_files_common_keys(tmp_env):
    a = tmp_env("a.env", "X=1\nY=2\n")
    b = tmp_env("b.env", "X=1\nY=2\n")
    c = tmp_env("c.env", "X=1\nY=2\nZ=3\n")
    result = compare_envs([a, b, c])
    assert result.common_keys == {"X", "Y"}
    assert "Z" not in result.common_keys
