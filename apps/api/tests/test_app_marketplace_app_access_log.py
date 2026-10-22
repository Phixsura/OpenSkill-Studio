from app.services.app_marketplace_app_access_log import create_access_log_entry, analyze_access_patterns

def test_create():
    e = create_access_log_entry(app_id="a1", user_id="u1", method="GET", path="/users",
                                 status_code=200, ip_address="1.2.3.4", user_agent="curl")
    assert e["method"] == "GET"
    assert e["ip_address"] == "1.2.3.4"

def test_analyze():
    logs = [{"path": "/users", "user_id": "u1", "status_code": 200},
            {"path": "/users", "user_id": "u2", "status_code": 200},
            {"path": "/apps", "user_id": "u1", "status_code": 404}]
    r = analyze_access_patterns(logs=logs)
    assert r["total_requests"] == 3
    assert r["unique_users"] == 2
    assert r["top_paths"][0][0] == "/users"
