from app.services.app_marketplace_app_app_app_app_app_app_app_restart_tracker import track_restarts

def test_track():
    r = track_restarts([
        {"name": "api", "restart_count": 0, "window_min": 60},
        {"name": "worker", "restart_count": 10, "window_min": 30},
    ])
    assert r["crash_loop_count"] == 1
    assert "worker" in r["crash_looping"]
    assert not r["all_stable"]

def test_stable():
    r = track_restarts([{"name": "api", "restart_count": 1, "window_min": 60}])
    assert r["all_stable"]
