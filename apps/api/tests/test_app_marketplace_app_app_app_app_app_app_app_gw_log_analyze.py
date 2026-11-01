from app.services.app_marketplace_app_app_app_app_app_app_app_gw_log_analyze import analyze_gateway_logs

def test_analyze():
    r = analyze_gateway_logs([
        {"path": "/api/users", "status": 200, "duration_ms": 50},
        {"path": "/api/users", "status": 200, "duration_ms": 60},
        {"path": "/api/orders", "status": 500, "duration_ms": 2000},
    ])
    assert r["total"] == 3
    assert r["by_status"]["2xx"] == 2
    assert r["by_status"]["5xx"] == 1
    assert r["slow_requests"] == 1
    assert r["top_paths"][0]["path"] == "/api/users"
