from app.services.app_marketplace_app_app_app_app_app_app_app_toggle_router import route_request, toggle_summary

def test_route():
    toggles = {
        "dark_mode": {"enabled": True, "rollout_pct": 100},
        "new_ui": {"enabled": True, "rollout_pct": 50},
        "beta": {"enabled": False},
    }
    r = route_request("user-123", toggles)
    assert r["flags"]["dark_mode"] is True
    assert r["flags"]["beta"] is False
    assert r["total_flags"] == 3

def test_summary():
    toggles = {
        "a": {"enabled": True, "rollout_pct": 100},
        "b": {"enabled": True, "rollout_pct": 50},
        "c": {"enabled": False},
    }
    r = toggle_summary(toggles)
    assert r["active"] == 2
    assert r["full_rollout"] == 1
    assert r["partial_rollout"] == 1
