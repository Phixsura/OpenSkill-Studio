from app.services.app_marketplace_api_playground_page import build_api_playground_page, build_request

def test_page():
    p = build_api_playground_page(
        collections=[{"name": "Auth Flow"}], environments=[{"name": "prod"}],
        recent_requests=[{"method": "GET", "url": "/apps"}])
    assert p["stats"]["collections"] == 1
    assert len(p["features"]) == 7

def test_request():
    r = build_request(method="GET", url="{{base_url}}/apps",
                        headers={"Authorization": "Bearer {{token}}"},
                        body=None, env={"base_url": "https://api.com", "token": "abc"})
    assert r["url"] == "https://api.com/apps"
    assert r["headers"]["Authorization"] == "Bearer abc"
    assert r["ready"]
