from app.services.app_marketplace_app_app_app_app_app_app_app_key_usage import analyze_key_usage

def test_usage():
    r = analyze_key_usage([
        {"api_key": "key_abc123", "endpoint": "/users", "status": 200},
        {"api_key": "key_abc123", "endpoint": "/orders", "status": 200},
        {"api_key": "key_abc123", "endpoint": "/users", "status": 400},
        {"api_key": "key_xyz789", "endpoint": "/users", "status": 200},
    ])
    assert r["total_keys"] == 2
    assert r["keys"][0]["requests"] == 3
    assert r["keys"][0]["unique_endpoints"] == 2
    assert r["keys"][0]["error_rate"] == 33.3
