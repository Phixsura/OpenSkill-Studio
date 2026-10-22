"""Parametrized conformance check status tests."""

import pytest
from app.services.conformance import ConformanceCheck, ConformanceReport

STATUSES = ["pass", "fail", "warn", "skip"]

@pytest.mark.parametrize("status", STATUSES)
def test_check_status(status):
    c = ConformanceCheck("test", status, "msg")
    assert c.status == status

@pytest.mark.parametrize("status", STATUSES)
def test_check_to_dict(status):
    c = ConformanceCheck("test", status, "msg", {"key": "val"})
    assert c.name == "test"
    assert c.details == {"key": "val"}

PASS_COMBOS = [
    (["pass"], True),
    (["pass", "warn"], True),
    (["pass", "skip"], True),
    (["pass", "warn", "skip"], True),
    (["fail"], False),
    (["pass", "fail"], False),
    (["warn", "fail"], False),
]

@pytest.mark.parametrize("statuses,expected", PASS_COMBOS)
def test_report_passed(statuses, expected):
    r = ConformanceReport(app_id="x", app_name="X", version="1.0.0")
    r.checks = [ConformanceCheck(f"c{i}", s, "msg") for i, s in enumerate(statuses)]
    assert r.passed == expected
