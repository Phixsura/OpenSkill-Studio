from app.services.app_marketplace_app_app_app_app_app_app_app_client_err import track_client_errors, client_error_rate

def test_track():
    r = track_client_errors([
        {"status": 400, "endpoint": "/api/users"},
        {"status": 404, "endpoint": "/api/users/999"},
        {"status": 400, "endpoint": "/api/users"},
        {"status": 422, "endpoint": "/api/orders"},
    ])
    assert r["total"] == 4
    assert r["by_status"][400] == 2
    assert r["top_endpoints"][0]["endpoint"] == "/api/users"

def test_rate():
    r = client_error_rate(10000, 200)
    assert r["rate_pct"] == 2.0
    assert r["healthy"]
