from app.services.app_marketplace_app_app_app_app_app_app_app_session_mgr import SessionManager

def test_create_validate():
    sm = SessionManager(ttl_seconds=60)
    r = sm.create("u1")
    token = r["token"]
    v = sm.validate(token)
    assert v["valid"]
    assert v["user_id"] == "u1"

def test_expired():
    sm = SessionManager(ttl_seconds=10)
    r = sm.create("u1")
    v = sm.validate(r["token"], now=time.time() + 11)
    assert not v["valid"]
    assert v["reason"] == "expired"

def test_revoke_user():
    sm = SessionManager()
    sm.create("u1")
    sm.create("u1")
    sm.create("u2")
    r = sm.revoke_user("u1")
    assert r["revoked"] == 2
    assert sm.stats()["active_sessions"] == 1

import time
