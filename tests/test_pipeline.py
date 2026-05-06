"""Tests for envsync.pipeline."""
from __future__ import annotations

import pathlib
import pytest

from envsync.pipeline import PipelineResult, run_pipeline


@pytest.fixture()
def tmp_env(tmp_path: pathlib.Path):
    def _write(name: str, content: str) -> pathlib.Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


# ---------------------------------------------------------------------------
# run_pipeline
# ---------------------------------------------------------------------------

def test_pipeline_returns_pipeline_result(tmp_env):
    p = tmp_env(".env", "API_KEY=hello\nDB_HOST=localhost\n")
    env = {"API_KEY": "hello", "DB_HOST": "localhost"}
    result = run_pipeline(str(p), env)
    assert isinstance(result, PipelineResult)


def test_pipeline_path_stored(tmp_env):
    p = tmp_env(".env", "FOO=bar\n")
    result = run_pipeline(str(p), {"FOO": "bar"})
    assert result.path == str(p)


def test_pipeline_no_issues_for_clean_env(tmp_env):
    p = tmp_env(".env", "FOO=bar\nBAZ=qux\n")
    env = {"FOO": "bar", "BAZ": "qux"}
    result = run_pipeline(str(p), env)
    assert not result.has_issues


def test_pipeline_audit_catches_empty_secret(tmp_env):
    p = tmp_env(".env", "SECRET=\n")
    result = run_pipeline(str(p), {"SECRET": ""})
    assert result.audit.has_issues
    assert result.has_issues


def test_pipeline_transform_steps_applied(tmp_env):
    p = tmp_env(".env", "FOO=  spaced  \n")
    env = {"FOO": "  spaced  "}
    result = run_pipeline(str(p), env, transform_steps=["strip_values"])
    assert result.transform.transformed["FOO"] == "spaced"


def test_pipeline_transform_steps_recorded(tmp_env):
    p = tmp_env(".env", "FOO=bar\n")
    steps = ["upper_keys", "strip_values"]
    result = run_pipeline(str(p), {"foo": "bar"}, transform_steps=steps)
    assert result.transform_steps == steps


def test_pipeline_summary_contains_path(tmp_env):
    p = tmp_env(".env", "KEY=value\n")
    result = run_pipeline(str(p), {"KEY": "value"})
    assert str(p) in result.summary()


def test_pipeline_summary_contains_lint_section(tmp_env):
    p = tmp_env(".env", "KEY=value\n")
    result = run_pipeline(str(p), {"KEY": "value"})
    assert "Lint" in result.summary()


def test_pipeline_summary_contains_audit_section(tmp_env):
    p = tmp_env(".env", "KEY=value\n")
    result = run_pipeline(str(p), {"KEY": "value"})
    assert "Audit" in result.summary()


def test_pipeline_summary_contains_transform_section(tmp_env):
    p = tmp_env(".env", "KEY=value\n")
    result = run_pipeline(str(p), {"KEY": "value"})
    assert "Transform" in result.summary()


def test_pipeline_empty_transform_steps_is_identity(tmp_env):
    p = tmp_env(".env", "KEY=value\n")
    env = {"KEY": "value"}
    result = run_pipeline(str(p), env, transform_steps=[])
    assert result.transform.transformed == env
