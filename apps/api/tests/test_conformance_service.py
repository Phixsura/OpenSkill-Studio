"""Conformance suite tests."""

import pytest
from dataclasses import fields
from app.services.conformance import (
    ConformanceCheck, ConformanceReport, run_conformance_checks,
)


def test_check_fields():
    actual = {f.name for f in fields(ConformanceCheck)}
    assert {"name", "passed", "message"}.issubset(actual)

def test_report_fields():
    actual = {f.name for f in fields(ConformanceReport)}
    assert {"checks"}.issubset(actual)

def test_report_all_passed():
    r = ConformanceReport(checks=[
        ConformanceCheck(name="a", passed=True, message="ok"),
        ConformanceCheck(name="b", passed=True, message="ok"),
    ])
    assert r.passed is True

def test_report_one_failed():
    r = ConformanceReport(checks=[
        ConformanceCheck(name="a", passed=True, message="ok"),
        ConformanceCheck(name="b", passed=False, message="fail"),
    ])
    assert r.passed is False

def test_report_summary():
    r = ConformanceReport(checks=[
        ConformanceCheck(name="a", passed=True, message="ok"),
    ])
    s = r.summary
    assert isinstance(s, dict)
    assert "total" in s or "passed" in s

def test_report_to_dict():
    r = ConformanceReport(checks=[
        ConformanceCheck(name="a", passed=True, message="ok"),
    ])
    d = r.to_dict()
    assert isinstance(d, dict)
    assert "checks" in d

def test_empty_report():
    r = ConformanceReport(checks=[])
    assert r.passed is True

def test_run_is_async():
    import inspect
    assert inspect.iscoroutinefunction(run_conformance_checks)
