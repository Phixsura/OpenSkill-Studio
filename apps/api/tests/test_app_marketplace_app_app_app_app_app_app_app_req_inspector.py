from app.services.app_marketplace_app_app_app_app_app_app_app_req_inspector import inspect_request, request_diff

def test_inspect():
    r = inspect_request("POST", "/api/users", {"Content-Type": "application/json", "Authorization": "Bearer x"},
                          body='{"name":"test"}', query_params={"page": "1"})
    assert r["method"] == "POST"
    assert r["auth_type"] == "bearer"
    assert r["body_size"] > 0
    assert r["param_count"] == 1

def test_diff():
    a = inspect_request("GET", "/api/users", {})
    b = inspect_request("POST", "/api/users", {"Content-Type": "application/json"}, body="x")
    r = request_diff(a, b)
    assert not r["identical"]
    assert r["diff_count"] >= 2
