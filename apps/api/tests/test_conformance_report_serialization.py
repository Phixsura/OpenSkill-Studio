"""ConformanceReport serialization edge cases."""

from app.services.conformance import ConformanceCheck, ConformanceReport


def _report(checks):
    return ConformanceReport(app_id="a", app_name="App", version="1.0.0",
                             checked_at="2026-01-01T00:00:00Z", checks=checks)

def test_to_dict_empty():
    r = _report([])
    d = r.to_dict()
    assert d["checks"] == []
    assert d["app_id"] == "a"

def test_to_dict_with_checks():
    r = _report([
        ConformanceCheck(name="manifest", status="pass", message="ok", details={}),
        ConformanceCheck(name="security", status="fail", message="weak", details={"issue": "no https"}),
    ])
    d = r.to_dict()
    assert len(d["checks"]) == 2
    assert d["checks"][0]["name"] == "manifest"
    assert d["checks"][1]["status"] == "fail"

def test_summary_counts():
    r = _report([
        ConformanceCheck(name="a", status="pass", message="ok", details={}),
        ConformanceCheck(name="b", status="pass", message="ok", details={}),
        ConformanceCheck(name="c", status="fail", message="bad", details={}),
    ])
    s = r.summary
    assert isinstance(s, dict)
    # Should have pass/fail counts
    total = s.get("total_checks", 0)
    assert total == 3

def test_passed_all_pass():
    r = _report([ConformanceCheck(name="a", status="pass", message="ok", details={})])
    assert r.passed is True

def test_passed_one_fail():
    r = _report([
        ConformanceCheck(name="a", status="pass", message="ok", details={}),
        ConformanceCheck(name="b", status="fail", message="bad", details={}),
    ])
    assert r.passed is False
