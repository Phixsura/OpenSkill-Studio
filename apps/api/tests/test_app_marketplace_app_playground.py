from app.services.app_marketplace_app_playground import create_playground_session, execute_playground_request, build_curl_command

def test_create():
    s = create_playground_session(app_id="a1", developer_id="d1", api_base="https://api.example.com")
    assert s["status"] == "active"

def test_execute():
    session = {"api_base": "https://api.example.com"}
    r = execute_playground_request(session=session, method="GET", path="/users")
    assert r["response"]["status_code"] == 200
    assert "api.example.com/users" in r["request"]["url"]

def test_curl():
    cmd = build_curl_command(method="POST", url="https://api.com/data",
                              headers={"Authorization": "Bearer token"}, body='{"key":"val"}')
    assert "curl -X POST" in cmd
    assert "Authorization" in cmd
    assert '{"key":"val"}' in cmd
