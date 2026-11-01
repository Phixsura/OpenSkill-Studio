from app.services.app_marketplace_app_app_app_app_app_app_app_user_session_trk import (
    create_session, get_active, revoke_session, session_stats, clear_sessions,
)

def test_create_and_get():
    clear_sessions()
    s1 = create_session("u1", "1.2.3.4", "Chrome")
    s2 = create_session("u1", "5.6.7.8", "Firefox")
    active = get_active("u1")
    assert len(active) == 2
    revoke_session(s1["session_id"])
    assert len(get_active("u1")) == 1
    clear_sessions()

def test_stats():
    clear_sessions()
    create_session("u1", "1.1.1.1")
    create_session("u2", "2.2.2.2")
    s = session_stats()
    assert s["active"] == 2
    assert s["unique_users"] == 2
    clear_sessions()
