"""Tests for envsync.reporter."""

from envsync.differ import DiffResult
from envsync.reporter import Report
from envsync.validator import ValidationResult


def _clean_validation(missing=None, extra=None) -> ValidationResult:
    vr = ValidationResult()
    vr.missing_keys = set(missing or [])
    vr.extra_keys = set(extra or [])
    return vr


def _make_diff(
    only_source=None,
    only_target=None,
    value_diffs=None,
) -> DiffResult:
    return DiffResult(
        only_in_source=set(only_source or []),
        only_in_target=set(only_target or []),
        value_diffs=value_diffs or {},
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def test_report_contains_file_paths():
    r = Report(source_file=".env.example", target_file=".env")
    text = r.render()
    assert ".env.example" in text
    assert ".env" in text


def test_report_has_title():
    r = Report(source_file="a", target_file="b")
    assert "EnvSync Report" in r.render()


# ---------------------------------------------------------------------------
# Validation section
# ---------------------------------------------------------------------------

def test_validation_pass_shown():
    r = Report("a", "b", validation=_clean_validation())
    assert "PASS" in r.render()


def test_validation_fail_shown():
    r = Report("a", "b", validation=_clean_validation(missing=["SECRET"]))
    assert "FAIL" in r.render()


def test_missing_keys_listed():
    r = Report("a", "b", validation=_clean_validation(missing=["SECRET", "TOKEN"]))
    text = r.render()
    assert "SECRET" in text
    assert "TOKEN" in text


def test_extra_keys_listed():
    r = Report("a", "b", validation=_clean_validation(extra=["UNUSED"]))
    assert "UNUSED" in r.render()


# ---------------------------------------------------------------------------
# Diff section
# ---------------------------------------------------------------------------

def test_diff_no_differences():
    r = Report("a", "b", diff=_make_diff())
    assert "no" in r.render()


def test_diff_only_source():
    r = Report("a", "b", diff=_make_diff(only_source=["NEW_KEY"]))
    assert "NEW_KEY" in r.render()


def test_diff_only_target():
    r = Report("a", "b", diff=_make_diff(only_target=["OLD_KEY"]))
    assert "OLD_KEY" in r.render()


def test_diff_value_diffs():
    r = Report("a", "b", diff=_make_diff(value_diffs={"PORT": ("8080", "9090")}))
    text = r.render()
    assert "PORT" in text
    assert "8080" in text
    assert "9090" in text


# ---------------------------------------------------------------------------
# has_issues
# ---------------------------------------------------------------------------

def test_no_issues_when_all_clean():
    r = Report(
        "a", "b",
        validation=_clean_validation(),
        diff=_make_diff(),
    )
    assert not r.has_issues()


def test_has_issues_when_validation_fails():
    r = Report("a", "b", validation=_clean_validation(missing=["X"]))
    assert r.has_issues()


def test_has_issues_when_diff_present():
    r = Report("a", "b", diff=_make_diff(only_source=["X"]))
    assert r.has_issues()
