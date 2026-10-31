from app.services.app_marketplace_app_request_inspector import inspect_request, compare_requests

def test_inspect():
    r = inspect_request(method="POST", path="/api/apps",
        headers={"Content-Type": "application/json", "Authorization": "Bearer sk_test"},
        body='{"name":"App"}', query_params={"v": "2"})
    assert r["method"] == "POST"
    assert r["has_auth"]
    assert r["auth_type"] == "Bearer"
    assert r["headers"]["Authorization"] == "***"
    assert r["body_size_bytes"] == 14

def test_no_auth():
    r = inspect_request(method="GET", path="/health", headers={})
    assert not r["has_auth"]

def test_compare():
    a = {"method": "GET", "path": "/a", "body_size_bytes": 0}
    b = {"method": "POST", "path": "/a", "body_size_bytes": 100}
    r = compare_requests(req_a=a, req_b=b)
    assert r["diff_count"] == 2
    assert not r["identical"]
