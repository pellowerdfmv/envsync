"""Tests for envsync.auditor."""

import pytest
from envsync.auditor import audit_env, AuditIssue, AuditResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _audit(env: dict, path: str = "test.env") -> AuditResult:
    return audit_env(path, env)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_clean_env_has_no_issues():
    result = _audit({"APP_NAME": "myapp", "DEBUG": "true", "PORT": "8080"})
    assert not result.has_issues


def test_empty_secret_is_error():
    result = _audit({"SECRET_KEY": ""})
    assert result.has_issues
    assert any(i.severity == "error" and i.key == "SECRET_KEY" for i in result.issues)


def test_none_password_is_error():
    result = _audit({"DB_PASSWORD": None})
    errors = result.errors
    assert len(errors) == 1
    assert errors[0].key == "DB_PASSWORD"


def test_placeholder_token_is_warning():
    result = _audit({"API_TOKEN": "changeme"})
    warnings = result.warnings
    assert len(warnings) == 1
    assert "placeholder" in warnings[0].message


def test_placeholder_detection_case_insensitive():
    result = _audit({"AUTH_KEY": "YOUR_KEY_HERE"})
    assert result.has_issues
    assert result.warnings[0].severity == "warning"


def test_placeholder_with_angle_brackets():
    result = _audit({"DATABASE_URL": "<your-dsn-here>"})
    assert result.has_issues


def test_non_sensitive_empty_key_not_flagged():
    result = _audit({"LOG_LEVEL": "", "FEATURE_FLAG": None})
    assert not result.has_issues


def test_multiple_issues_collected():
    result = _audit({
        "SECRET_KEY": "",
        "DB_PASSWORD": "changeme",
        "API_TOKEN": None,
    })
    assert len(result.issues) == 3


def test_summary_no_issues():
    result = _audit({"NAME": "ok"})
    assert "no issues" in result.summary()


def test_summary_with_issues():
    result = _audit({"SECRET_KEY": ""})
    summary = result.summary()
    assert "ERROR" in summary
    assert "SECRET_KEY" in summary


def test_audit_result_path_preserved():
    result = audit_env("prod.env", {"APP": "x"})
    assert result.path == "prod.env"


def test_errors_and_warnings_split_correctly():
    result = _audit({
        "DB_PASSWORD": None,       # error
        "API_TOKEN": "example",    # warning
    })
    assert len(result.errors) == 1
    assert len(result.warnings) == 1
