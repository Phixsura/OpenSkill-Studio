from app.services.app_marketplace_app_app_app_app_app_app_app_api_usage_brkdn import compute_usage_breakdown

def test_breakdown():
    reqs = [
        {"method": "GET", "path": "/users", "duration_ms": 50, "status": 200},
        {"method": "GET", "path": "/users", "duration_ms": 60, "status": 200},
        {"method": "POST", "path": "/apps", "duration_ms": 120, "status": 201},
        {"method": "GET", "path": "/users", "duration_ms": 45, "status": 500},
    ]
    r = compute_usage_breakdown(reqs)
    assert r["total_requests"] == 4
    assert r["unique_endpoints"] == 2
    users = next(b for b in r["breakdown"] if "users" in b["endpoint"])
    assert users["count"] == 3
    assert users["errors"] == 1
    assert users["error_pct"] > 0
