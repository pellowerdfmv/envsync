"""Tests for envsync.linter."""
from __future__ import annotations

import os
import pytest

from envsync.linter import lint_env, LintResult


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(p, text: str):
    p.write_text(text, encoding='utf-8')
    return str(p)


def test_clean_file_has_no_issues(tmp_env):
    path = _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\n")
    result = lint_env(path, {})
    assert not result.has_issues()


def test_lower_case_key_is_warning(tmp_env):
    path = _write(tmp_env, "db_host=localhost\n")
    result = lint_env(path, {})
    codes = [i.code for i in result.issues]
    assert 'W002' in codes


def test_mixed_case_key_is_warning(tmp_env):
    path = _write(tmp_env, "DbHost=localhost\n")
    result = lint_env(path, {})
    codes = [i.code for i in result.issues]
    assert 'W002' in codes


def test_leading_whitespace_is_error(tmp_env):
    path = _write(tmp_env, "  DB_HOST=localhost\n")
    result = lint_env(path, {})
    codes = [i.code for i in result.issues]
    assert 'E001' in codes


def test_duplicate_key_is_error(tmp_env):
    path = _write(tmp_env, "DB_HOST=localhost\nDB_HOST=remote\n")
    result = lint_env(path, {})
    errors = [i for i in result.issues if i.code == 'E002']
    assert len(errors) == 1
    assert errors[0].key == 'DB_HOST'


def test_trailing_whitespace_on_value_is_warning(tmp_env):
    path = _write(tmp_env, "DB_HOST=localhost   \n")
    result = lint_env(path, {})
    codes = [i.code for i in result.issues]
    assert 'W003' in codes


def test_comments_and_blank_lines_skipped(tmp_env):
    path = _write(tmp_env, "# comment\n\nDB_HOST=localhost\n")
    result = lint_env(path, {})
    assert not result.has_issues()


def test_summary_format(tmp_env):
    path = _write(tmp_env, "db_host=localhost\nDB_HOST=remote\nDB_HOST=other\n")
    result = lint_env(path, {})
    s = result.summary()
    assert 'error' in s
    assert 'warning' in s


def test_errors_and_warnings_filtered(tmp_env):
    path = _write(tmp_env, "db_host=localhost\nDB_HOST=a\nDB_HOST=b\n")
    result = lint_env(path, {})
    assert all(i.severity == 'error' for i in result.errors())
    assert all(i.severity == 'warning' for i in result.warnings())


def test_lint_result_path_stored(tmp_env):
    path = _write(tmp_env, "DB_HOST=localhost\n")
    result = lint_env(path, {})
    assert result.path == path
