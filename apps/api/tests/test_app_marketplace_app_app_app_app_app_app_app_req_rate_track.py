from app.services.app_marketplace_app_app_app_app_app_app_app_req_rate_track import track_request_rates

def test_track():
    r = track_request_rates([
        {"path": "/api/users", "rps": 500, "status_counts": {"200": 490, "500": 10}},
        {"path": "/api/orders", "rps": 200, "status_counts": {"200": 195, "404": 5}},
    ])
    assert r["total_rps"] == 700
    assert r["error_rps"] == 10
    assert r["endpoint_count"] == 2
