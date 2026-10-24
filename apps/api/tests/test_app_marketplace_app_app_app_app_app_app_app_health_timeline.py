from app.services.app_marketplace_app_app_app_app_app_app_app_health_timeline import build_timeline, compare_periods

def test_timeline():
    entries = [{"status": "healthy"}] * 9 + [{"status": "degraded"}]
    r = build_timeline(entries)
    assert r["uptime_pct"] == 90.0
    assert r["incidents"] == 1

def test_compare():
    c = build_timeline([{"status": "healthy"}] * 10)
    p = build_timeline([{"status": "healthy"}] * 8 + [{"status": "down"}] * 2)
    r = compare_periods(c, p)
    assert r["improving"]
    assert r["delta"] == 20.0
