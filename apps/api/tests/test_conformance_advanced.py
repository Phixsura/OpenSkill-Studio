"""Advanced conformance suite tests."""

from app.services.conformance import ConformanceCheck, ConformanceReport


def test_conformance_check_structure():
    check = ConformanceCheck(name="test", status="pass", message="OK")
    assert check.name == "test"
    assert check.status == "pass"
    assert check.details == {}


def test_conformance_check_with_details():
    check = ConformanceCheck(name="test", status="fail", message="Bad", details={"errors": ["e1"]})
    assert check.details["errors"] == ["e1"]


def test_conformance_report_passed():
    report = ConformanceReport(app_id="a1", app_name="Test", version="1.0.0")
    report.checks = [
        ConformanceCheck("c1", "pass", "OK"),
        ConformanceCheck("c2", "pass", "OK"),
        ConformanceCheck("c3", "warn", "Minor"),
        ConformanceCheck("c4", "skip", "N/A"),
    ]
    assert report.passed is True
    s = report.summary
    assert s["pass"] == 2
    assert s["warn"] == 1
    assert s["skip"] == 1
    assert s["fail"] == 0
    assert s["total_checks"] == 4


def test_conformance_report_failed():
    report = ConformanceReport(app_id="a2", app_name="Test", version="1.0.0")
    report.checks = [
        ConformanceCheck("c1", "pass", "OK"),
        ConformanceCheck("c2", "fail", "Bad"),
    ]
    assert report.passed is False
    assert report.summary["fail"] == 1


def test_conformance_report_to_dict():
    report = ConformanceReport(app_id="a3", app_name="Dict", version="2.0.0")
    report.checks = [ConformanceCheck("c1", "pass", "OK")]
    d = report.to_dict()
    assert d["app_id"] == "a3"
    assert d["app_name"] == "Dict"
    assert d["version"] == "2.0.0"
    assert d["checked_at"]
    assert len(d["checks"]) == 1
    assert d["summary"]["passed"] is True


def test_conformance_report_empty():
    report = ConformanceReport(app_id="a4", app_name="Empty", version="0.0.0")
    assert report.passed is True
    assert report.summary["total_checks"] == 0
