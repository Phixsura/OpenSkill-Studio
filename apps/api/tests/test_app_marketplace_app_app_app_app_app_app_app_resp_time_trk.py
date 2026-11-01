from app.services.app_marketplace_app_app_app_app_app_app_app_resp_time_trk import track_response_times, compare_endpoints

def test_track():
    r = track_response_times("/api/users", [50, 80, 120, 200, 600])
    assert r["count"] == 5
    assert r["slow_count"] == 1
    assert r["slow_pct"] == 20.0

def test_compare():
    endpoints = [
        track_response_times("/fast", [10, 20, 30]),
        track_response_times("/slow", [500, 800, 1200]),
    ]
    r = compare_endpoints(endpoints)
    assert r["slowest"] == "/slow"
    assert r["fastest"] == "/fast"
