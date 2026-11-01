from app.services.app_marketplace_app_app_session_manager import create_session, list_sessions, revoke_session

def test_create():
    r = create_session(user_id="u1", device="Chrome on Mac", ip="1.2.3.4")
    assert r["active"]
    assert len(r["token"]) > 30

def test_list():
    s1 = create_session(user_id="u1", device="Chrome", ip="1.1.1.1")
    s2 = create_session(user_id="u1", device="Firefox", ip="2.2.2.2")
    r = list_sessions(sessions=[s1, s2], current_token=s1["token"])
    assert r["active"] == 2
    assert r["sessions"][0]["is_current"]

def test_revoke():
    s = create_session(user_id="u1", device="X", ip="0.0.0.0")
    r = revoke_session(sessions=[s], token=s["token"])
    assert r["revoked"]
    assert not s["active"]
