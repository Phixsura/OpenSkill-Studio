from app.services.app_marketplace_app_app_app_app_app_app_app_avail_report import generate_availability_report

def test_report():
    r = generate_availability_report([
        {"name": "api", "uptime_pct": 99.95, "sla_target": 99.9, "incidents": 2},
        {"name": "web", "uptime_pct": 99.5, "sla_target": 99.9, "incidents": 5},
    ])
    assert r["sla_breaches"] == 1
    assert not r["all_sla_met"]
    assert r["avg_uptime"] == 99.725
    assert r["services"][1]["downtime_min"] > 0
