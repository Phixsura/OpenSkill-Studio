"""Health monitor + conformance integration test."""

from app.services.app_health_monitor import HealthScore
from app.services.conformance import ConformanceCheck, ConformanceReport


def test_health_drives_conformance():
    """HealthScore results feed into conformance checks."""
    for total, failed, timeout, expected_pass in [
        (1000, 10, 5, True),    # healthy → pass
        (100, 60, 0, False),    # critical → fail
    ]:
        h = HealthScore(total, failed, timeout)
        check = ConformanceCheck(
            name="app_health",
            status="pass" if h.score >= 50 else "fail",
            message=f"Score: {h.score} ({h.status})",
            details=h.to_dict(),
        )
        report = ConformanceReport(
            app_id="test", app_name="Test", version="1.0.0",
            checked_at="2026-01-01T00:00:00Z", checks=[check],
        )
        assert report.passed is expected_pass
        d = report.to_dict()
        assert d["checks"][0]["details"]["score"] == h.score


def test_multi_check_report():
    """Multiple conformance checks from different sources."""
    checks = [
        ConformanceCheck(name="manifest", status="pass", message="Valid", details={}),
        ConformanceCheck(name="security", status="pass", message="No issues", details={}),
        ConformanceCheck(name="health", status="pass", message="Score: 98", details={"score": 98}),
    ]
    r = ConformanceReport(app_id="a", app_name="A", version="1.0.0",
                          checked_at="now", checks=checks)
    assert r.passed is True
    assert r.summary["total_checks"] == 3
    assert r.summary["pass"] == 3
