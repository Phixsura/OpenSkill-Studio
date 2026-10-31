from app.services.app_marketplace_app_app_api_playground import build_request, simulate_response

def test_build():
    r = build_request(method="POST", url="https://api.example.com/apps",
                      headers={"Authorization": "Bearer tok"}, body='{"name":"App"}')
    assert r["method"] == "POST"
    assert "curl" in r
    assert r["has_body"]

def test_bad_scheme():
    r = build_request(method="GET", url="ftp://bad")
    assert "error" in r

def test_response():
    r = simulate_response(status=201, body={"id": "app_1"})
    assert r["success"]
    assert r["status"] == 201
    assert "app_1" in r["body"]
