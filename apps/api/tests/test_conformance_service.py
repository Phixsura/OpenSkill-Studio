"""Conformance suite tests."""

import pytest
from dataclasses import fields
from app.services.conformance import (
    ConformanceCheck, ConformanceReport, run_conformance_checks,
)

def test_check_fields():
    actual = {f.name for f in fields(ConformanceCheck)}
    assert {"name", "status", "message", "details"}.issubset(actual)

def test_report_fields():
    actual = {f.name for f in fields(ConformanceReport)}
    assert {"app_id", "app_name", "version", "checks"}.issubset(actual)

def _make_report(checks):
    return ConformanceReport(app_id="a", app_name="Test", version="1.0.0",
                             checked_at="2026-01-01T00:00:00Z", checks=checks)

def test_report_all_passed():
    r = _make_report([ConformanceCheck(name="a", status="pass", message="ok", details={})])
    assert r.passed is True

def test_report_one_failed():
    r = _make_report([
        ConformanceCheck(name="a", status="pass", message="ok", details={}),
        ConformanceCheck(name="b", status="fail", message="bad", details={}),
    ])
    assert r.passed is False

def test_report_summary():
    r = _make_report([ConformanceCheck(name="a", status="pass", message="ok", details={})])
    s = r.summary
    assert isinstance(s, dict)

def test_report_to_dict():
    r = _make_report([ConformanceCheck(name="a", status="pass", message="ok", details={})])
    d = r.to_dict()
    assert isinstance(d, dict)
    assert "checks" in d

def test_empty_report():
    r = _make_report([])
    assert r.passed is True

def test_run_is_async():
    import inspect
    assert inspect.iscoroutinefunction(run_conformance_checks)
