from app.services.app_marketplace_app_app_app_app_app_app_app_uptime_report import generate_report

def test_report():
    r = generate_report([
        {"name": "api", "uptime_pct": 99.99, "incidents": 1, "downtime_minutes": 5, "sla_target": 99.9},
        {"name": "web", "uptime_pct": 100, "incidents": 0, "downtime_minutes": 0, "sla_target": 99.9},
        {"name": "worker", "uptime_pct": 99.5, "incidents": 3, "downtime_minutes": 216, "sla_target": 99.9},
    ])
    assert r["total_services"] == 3
    assert not r["all_sla_met"]  # worker below SLA
    assert r["services"][2]["sla_met"] is False
    assert r["avg_uptime_pct"] > 99
