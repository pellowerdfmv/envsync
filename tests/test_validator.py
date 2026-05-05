"""Unit tests for envsync.validator."""

import textwrap
import pytest
from pathlib import Path

from envsync.validator import validate, ValidationResult


@pytest.fixture()
def env_files(tmp_path):
    """Helper to create named env files in a temp directory."""
    def _write(name: str, content: str) -> str:
        p: Path = tmp_path / name
        p.write_text(textwrap.dedent(content), encoding='utf-8')
        return str(p)
    return _write


def test_valid_env_passes(env_files):
    example = env_files('.env.example', 'APP_KEY=somevalue\nDEBUG=true\n')
    env = env_files('.env', 'APP_KEY=realvalue\nDEBUG=false\n')
    result = validate(env, example)
    assert result.is_valid
    assert result.missing_keys == []
    assert result.extra_keys == []


def test_missing_key_detected(env_files):
    example = env_files('.env.example', 'APP_KEY=x\nSECRET=y\n')
    env = env_files('.env', 'APP_KEY=real\n')
    result = validate(env, example)
    assert not result.is_valid
    assert 'SECRET' in result.missing_keys


def test_extra_key_reported(env_files):
    example = env_files('.env.example', 'APP_KEY=x\n')
    env = env_files('.env', 'APP_KEY=real\nEXTRA=surprise\n')
    result = validate(env, example)
    assert result.is_valid  # extra keys don't fail by default
    assert 'EXTRA' in result.extra_keys


def test_strict_mode_fails_on_extra(env_files):
    example = env_files('.env.example', 'APP_KEY=x\n')
    env = env_files('.env', 'APP_KEY=real\nEXTRA=surprise\n')
    result = validate(env, example, strict=True)
    assert result.extra_keys == ['EXTRA']


def test_empty_required_key_detected(env_files):
    example = env_files('.env.example', 'DATABASE_URL=postgres://localhost/db\n')
    env = env_files('.env', 'DATABASE_URL=\n')
    result = validate(env, example)
    assert not result.is_valid
    assert 'DATABASE_URL' in result.empty_required_keys


def test_summary_all_clear(env_files):
    example = env_files('.env.example', 'KEY=val\n')
    env = env_files('.env', 'KEY=realval\n')
    result = validate(env, example)
    assert result.summary() == 'All checks passed.'


def test_file_not_found_propagates(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate(str(tmp_path / 'missing.env'), str(tmp_path / 'missing.example'))
