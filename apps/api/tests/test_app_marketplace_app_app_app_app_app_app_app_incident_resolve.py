from app.services.app_marketplace_app_app_app_app_app_app_app_incident_resolve import should_auto_resolve, resolution_summary

def test_resolve():
    r = should_auto_resolve({"id": "inc-1"},
        {"error_rate_pct": 0.1, "p99_ms": 100, "baseline_p99_ms": 200,
         "uptime_pct": 99.99, "active_alerts": 0})
    assert r["auto_resolve"]
    assert r["recommendation"] == "resolve"

def test_keep_open():
    r = should_auto_resolve({"id": "inc-2"},
        {"error_rate_pct": 5, "p99_ms": 800, "baseline_p99_ms": 200,
         "uptime_pct": 98, "active_alerts": 2})
    assert not r["auto_resolve"]

def test_summary():
    r = resolution_summary([
        {"auto_resolved": True, "resolved": True},
        {"auto_resolved": False, "resolved": True},
        {"resolved": False},
    ])
    assert r["auto_resolved"] == 1
    assert r["manual_resolved"] == 1
    assert r["open"] == 1
