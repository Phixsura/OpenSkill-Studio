from app.services.app_marketplace_app_app_app_app_app_app_app_uptime_mon import calculate_uptime, uptime_summary

def test_uptime():
    checks = [{"status": "up"}] * 999 + [{"status": "down", "duration_sec": 60}]
    r = calculate_uptime(checks)
    assert r["uptime_pct"] == 99.9
    assert r["total_downtime_sec"] == 60
    assert r["sla_met"]

def test_summary():
    monitors = [
        {"name": "api", "uptime_pct": 99.99, "sla_met": True},
        {"name": "db", "uptime_pct": 99.5, "sla_met": False},
    ]
    r = uptime_summary(monitors)
    assert not r["all_sla_met"]
    assert r["worst_service"] == "db"
