"""Tests for envsync.differ module."""

import pytest

from envsync.differ import DiffResult, diff_envs


SOURCE = {"APP_NAME": "myapp", "DEBUG": "true", "SECRET_KEY": "abc123"}
TARGET = {"APP_NAME": "myapp", "DEBUG": "false", "DATABASE_URL": "postgres://localhost/db"}


def test_only_in_source_detected():
    result = diff_envs(SOURCE, TARGET)
    assert "SECRET_KEY" in result.only_in_source


def test_only_in_target_detected():
    result = diff_envs(SOURCE, TARGET)
    assert "DATABASE_URL" in result.only_in_target


def test_no_value_diff_by_default():
    result = diff_envs(SOURCE, TARGET)
    assert result.value_changed == {}


def test_value_diff_when_enabled():
    result = diff_envs(SOURCE, TARGET, compare_values=True)
    assert "DEBUG" in result.value_changed
    assert result.value_changed["DEBUG"] == ("true", "false")


def test_identical_envs_no_differences():
    env = {"FOO": "bar", "BAZ": None}
    result = diff_envs(env, env.copy(), compare_values=True)
    assert not result.has_differences


def test_has_differences_true_when_keys_differ():
    result = diff_envs(SOURCE, TARGET)
    assert result.has_differences


def test_summary_contains_plus_for_source_only():
    result = diff_envs(SOURCE, TARGET)
    summary = result.summary()
    assert "+ SECRET_KEY" in summary


def test_summary_contains_minus_for_target_only():
    result = diff_envs(SOURCE, TARGET)
    summary = result.summary()
    assert "- DATABASE_URL" in summary


def test_summary_contains_tilde_for_changed_values():
    result = diff_envs(SOURCE, TARGET, compare_values=True)
    summary = result.summary()
    assert "~ DEBUG" in summary


def test_summary_no_differences_message():
    env = {"KEY": "val"}
    result = diff_envs(env, env.copy())
    assert result.summary() == "  No differences found."


def test_none_values_compared_correctly():
    src = {"EMPTY": None}
    tgt = {"EMPTY": "something"}
    result = diff_envs(src, tgt, compare_values=True)
    assert "EMPTY" in result.value_changed
    assert result.value_changed["EMPTY"] == (None, "something")
