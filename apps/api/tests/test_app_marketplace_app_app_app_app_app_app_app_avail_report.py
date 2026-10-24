from app.services.app_marketplace_app_app_app_app_app_app_app_avail_report import generate_availability_report

def test_report():
    r = generate_availability_report([
        {"name": "api", "uptime_pct": 99.99, "downtime_minutes": 5, "incidents": 1, "sla_target": 99.9},
        {"name": "db", "uptime_pct": 99.5, "downtime_minutes": 216, "incidents": 3, "sla_target": 99.9},
    ], period="October 2026")
    assert r["period"] == "October 2026"
    assert r["sla_breaches"] == 1
    assert not r["all_sla_met"]
    assert r["total_incidents"] == 4
    assert r["services"][0]["service"] == "db"  # sorted by uptime
