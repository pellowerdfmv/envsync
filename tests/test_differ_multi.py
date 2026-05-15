"""Tests for envsync.differ_multi and envsync.cli_differ_multi."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envsync.differ_multi import diff_multi, MultiDiffResult, MultiDiffEntry
from envsync.cli_differ_multi import cmd_multi_diff


# ------------------------------------------------------------------ helpers --


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a factory that writes an env file and returns its Path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


# ------------------------------------------------------------------ unit -----


def test_returns_multi_diff_result(tmp_env):
    ref = tmp_env("ref.env", "A=1\nB=2\n")
    t1 = tmp_env("t1.env", "A=1\nB=2\n")
    result = diff_multi(ref, [t1])
    assert isinstance(result, MultiDiffResult)


def test_len_equals_number_of_targets(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    t1 = tmp_env("t1.env", "A=1\n")
    t2 = tmp_env("t2.env", "A=1\n")
    result = diff_multi(ref, [t1, t2])
    assert len(result) == 2


def test_identical_target_has_no_differences(tmp_env):
    ref = tmp_env("ref.env", "A=1\nB=2\n")
    t1 = tmp_env("t1.env", "A=1\nB=2\n")
    result = diff_multi(ref, [t1])
    assert not result.has_differences()


def test_missing_key_in_target_detected(tmp_env):
    ref = tmp_env("ref.env", "A=1\nB=2\n")
    t1 = tmp_env("t1.env", "A=1\n")
    result = diff_multi(ref, [t1])
    assert result.has_differences()


def test_extra_key_in_target_detected(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    t1 = tmp_env("t1.env", "A=1\nEXTRA=99\n")
    result = diff_multi(ref, [t1])
    assert result.has_differences()


def test_entries_contain_correct_paths(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    t1 = tmp_env("t1.env", "A=1\n")
    result = diff_multi(ref, [t1])
    assert result.entries[0].target_path == t1
    assert result.reference_path == ref


def test_summary_contains_reference_path(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    t1 = tmp_env("t1.env", "A=1\n")
    result = diff_multi(ref, [t1])
    assert str(ref) in result.summary()


def test_summary_shows_in_sync(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    t1 = tmp_env("t1.env", "A=1\n")
    result = diff_multi(ref, [t1])
    assert "in sync" in result.summary()


def test_summary_shows_differs(tmp_env):
    ref = tmp_env("ref.env", "A=1\nB=2\n")
    t1 = tmp_env("t1.env", "A=1\n")
    result = diff_multi(ref, [t1])
    assert "differs" in result.summary()


# ------------------------------------------------------------------ CLI ------


def _make_args(reference, targets, values=False, strict=False):
    ns = argparse.Namespace(
        reference=reference,
        targets=targets,
        values=values,
        strict=strict,
    )
    return ns


def test_cmd_multi_diff_returns_zero_for_identical(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    t1 = tmp_env("t1.env", "A=1\n")
    assert cmd_multi_diff(_make_args(ref, [t1])) == 0


def test_cmd_multi_diff_missing_reference_returns_one(tmp_path):
    ref = tmp_path / "ghost.env"
    t1 = tmp_path / "t1.env"
    t1.write_text("A=1\n")
    assert cmd_multi_diff(_make_args(ref, [t1])) == 1


def test_cmd_multi_diff_missing_target_returns_one(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    ghost = ref.parent / "ghost.env"
    assert cmd_multi_diff(_make_args(ref, [ghost])) == 1


def test_cmd_multi_diff_strict_returns_one_on_diff(tmp_env):
    ref = tmp_env("ref.env", "A=1\nB=2\n")
    t1 = tmp_env("t1.env", "A=1\n")
    assert cmd_multi_diff(_make_args(ref, [t1], strict=True)) == 1


def test_cmd_multi_diff_strict_returns_zero_when_identical(tmp_env):
    ref = tmp_env("ref.env", "A=1\n")
    t1 = tmp_env("t1.env", "A=1\n")
    assert cmd_multi_diff(_make_args(ref, [t1], strict=True)) == 0
