from app.services.app_marketplace_app_user_session import create_session, list_active_sessions, revoke_session

def test_create():
    r = create_session(user_id="u1", ip="1.2.3.4", user_agent="Chrome/120", device_type="desktop")
    assert len(r["session_id"]) > 20
    assert r["active"]

def test_list():
    sessions = [{"active": True, "device_type": "desktop"}, {"active": True, "device_type": "mobile"},
                {"active": False, "device_type": "desktop"}]
    r = list_active_sessions(sessions=sessions)
    assert r["total_active"] == 2
    assert r["by_device"]["desktop"] == 1

def test_revoke():
    sessions = [{"session_hash": "abc", "active": True}]
    r = revoke_session(session_hash="abc", sessions=sessions)
    assert r["revoked"]
    assert not sessions[0]["active"]

def test_revoke_not_found():
    r = revoke_session(session_hash="xyz", sessions=[])
    assert "error" in r
