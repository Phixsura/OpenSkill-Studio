from app.services.app_marketplace_app_app_app_app_app_app_app_request_replay import (
    capture_request, replay_request, list_captures, clear_captures,
)

def test_capture_replay():
    clear_captures()
    c = capture_request("POST", "/api/v1/users", {"Content-Type": "application/json", "Authorization": "Bearer x"}, '{"name":"test"}')
    assert "Authorization" not in c["headers"]  # stripped
    r = replay_request(c["id"])
    assert r["replayed"]
    assert r["method"] == "POST"
    clear_captures()

def test_list():
    clear_captures()
    capture_request("GET", "/a", {})
    capture_request("POST", "/b", {})
    caps = list_captures()
    assert len(caps) == 2
    assert caps[0]["path"] == "/b"  # most recent first
    clear_captures()
