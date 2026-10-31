from app.services.app_marketplace_app_uptime_monitor import record_check, compute_uptime_stats, build_uptime_calendar

def test_healthy_check():
    r = record_check(endpoint="/health", status_code=200, response_ms=50)
    assert r["healthy"]

def test_unhealthy_check():
    r = record_check(endpoint="/health", status_code=500, response_ms=100)
    assert not r["healthy"]

def test_stats():
    checks = [{"healthy": True, "response_ms": 100}] * 99 + [{"healthy": False, "response_ms": 5000}]
    s = compute_uptime_stats(checks=checks)
    assert s["uptime_pct"] == 99.0
    assert s["downtime_minutes"] == 1

def test_calendar():
    daily = [{"date": "2026-01-01", "uptime_pct": 100}, {"date": "2026-01-02", "uptime_pct": 98}]
    c = build_uptime_calendar(daily_uptimes=daily)
    assert c[0]["status"] == "good"
    assert c[1]["status"] == "outage"
