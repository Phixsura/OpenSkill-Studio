from app.services.app_marketplace_app_app_app_app_app_app_app_api_playground import build_request, simulate_response

def test_build():
    r = build_request(method="POST", path="/api/v1/apps",
                       body='{"name": "test"}')
    assert r["valid"]
    assert r["method"] == "POST"
    assert "curl" in r
    assert r["body"]["name"] == "test"

def test_invalid_method():
    r = build_request(method="TRACE", path="/x")
    assert not r["valid"]

def test_simulate():
    req = build_request(method="GET", path="/api/v1/apps")
    resp = simulate_response(req)
    assert resp["status"] == 200
    resp2 = simulate_response(build_request(method="DELETE", path="/api/v1/apps/1"))
    assert resp2["status"] == 204
