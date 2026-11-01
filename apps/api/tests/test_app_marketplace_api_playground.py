from app.services.app_marketplace_api_playground import list_playground_endpoints, simulate_request

def test_list():
    r = list_playground_endpoints()
    assert r["total"] == 7
    assert "GET" in r["methods"]

def test_filter_auth():
    r = list_playground_endpoints(auth=True)
    assert all(e["auth_required"] for e in r["endpoints"])

def test_simulate():
    r = simulate_request(method="GET", path="/api/v1/apps")
    assert r["status"] == 200
    assert "request_id" in r["body"]["data"]

def test_simulate_auth():
    r = simulate_request(method="POST", path="/api/v1/apps")
    assert r["status"] == 401

def test_simulate_with_key():
    r = simulate_request(method="POST", path="/api/v1/apps", api_key="sk_test")
    assert r["status"] == 200
