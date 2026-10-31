from app.services.app_marketplace_app_app_app_app_app_app_app_gw_transform import transform_request

def test_transform():
    r = transform_request(
        {"path": "/api/v1/users", "headers": {"Content-Type": "application/json"}},
        [{"action": "add_header", "key": "X-Request-ID", "value": "123"},
         {"action": "rewrite_path", "from": "/api/v1", "to": "/internal/v1"},
         {"action": "set_timeout", "value": 3000}])
    assert r["request"]["headers"]["X-Request-ID"] == "123"
    assert r["request"]["path"] == "/internal/v1/users"
    assert r["request"]["timeout_ms"] == 3000
    assert r["count"] == 3

def test_remove_header():
    r = transform_request(
        {"headers": {"Authorization": "Bearer xxx", "X-Debug": "true"}},
        [{"action": "remove_header", "key": "X-Debug"}])
    assert "X-Debug" not in r["request"]["headers"]
