from app.services.app_developer_api_playground import get_playground_endpoints, build_curl_command

def test_endpoints():
    eps = get_playground_endpoints()
    assert len(eps) >= 5

def test_curl_get():
    ep = {"method": "GET", "path": "/api/v1/apps", "auth": True}
    curl = build_curl_command(ep)
    assert "curl" in curl
    assert "Authorization" in curl

def test_curl_post():
    ep = {"method": "POST", "path": "/api/v1/apps", "auth": True, "body": {"name": "X"}}
    curl = build_curl_command(ep)
    assert "POST" in curl
    assert "Content-Type" in curl

def test_curl_no_auth():
    ep = {"method": "GET", "path": "/api/v1/marketplace", "auth": False}
    curl = build_curl_command(ep)
    assert "Authorization" not in curl
