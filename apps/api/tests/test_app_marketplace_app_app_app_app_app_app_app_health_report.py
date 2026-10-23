from app.services.app_marketplace_app_app_app_app_app_app_app_health_report import generate_report

def test_report():
    r = generate_report(
        [{"status": "healthy"}, {"status": "healthy"}, {"status": "degraded"}],
        [{"status": "resolved"}, {"status": "open"}],
        sla_compliance=99.5, uptime_pct=99.9)
    assert r["services"]["healthy"] == 2
    assert r["incidents"]["open"] == 1
    assert r["grade"] in ("A", "B", "C")
    assert r["score"] > 0
