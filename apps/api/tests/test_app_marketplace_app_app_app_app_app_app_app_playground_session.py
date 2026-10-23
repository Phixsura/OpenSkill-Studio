from app.services.app_marketplace_app_app_app_app_app_app_app_playground_session import PlaygroundSession

def test_session():
    ps = PlaygroundSession()
    s = ps.create(user_id="alice")
    ps.add_request(s["session_id"], method="GET", path="/api/apps", status=200, duration_ms=85)
    ps.add_request(s["session_id"], method="POST", path="/api/apps", status=201, duration_ms=120)
    ps.set_variable(s["session_id"], "app_id", "test123")
    session = ps.get_session(s["session_id"], user_id="alice")
    assert len(session["history"]) == 2
    assert session["variables"]["app_id"] == "test123"
