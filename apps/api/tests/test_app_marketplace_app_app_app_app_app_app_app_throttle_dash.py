from app.services.app_marketplace_app_app_app_app_app_app_app_throttle_dash import build_throttle_dashboard

def test_dashboard():
    r = build_throttle_dashboard([
        {"path": "/api/users", "blocked_count": 0, "limit": 100, "current_rps": 50},
        {"path": "/api/search", "blocked_count": 150, "limit": 50, "current_rps": 80},
        {"path": "/api/export", "blocked_count": 30, "limit": 10, "current_rps": 15},
    ])
    assert r["healthy"] == 1
    assert r["throttled_count"] == 2
    assert r["total_blocked"] == 180
    assert r["status"] == "throttling"
