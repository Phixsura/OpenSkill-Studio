from app.services.app_marketplace_app_app_app_app_app_app_app_svc_level_rpt import generate_service_level_report

def test_report():
    r = generate_service_level_report([
        {"name": "api", "uptime_pct": 99.99, "error_rate_pct": 0.1, "slo_met": True, "incidents": 1, "downtime_min": 5},
        {"name": "db", "uptime_pct": 99.5, "error_rate_pct": 0.5, "slo_met": False, "incidents": 3, "downtime_min": 216},
        {"name": "web", "uptime_pct": 100, "error_rate_pct": 0, "slo_met": True, "incidents": 0, "downtime_min": 0},
    ], period="Q4 2026")
    assert r["period"] == "Q4 2026"
    assert r["slo_met"] == 2
    assert r["slo_breached"] == 1
    assert r["total_incidents"] == 4
    assert r["compliance_pct"] == 66.7
    assert "1 SLO breaches" in r["executive_summary"]
