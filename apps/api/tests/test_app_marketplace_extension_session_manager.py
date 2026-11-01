from app.services.app_marketplace_extension_session_manager import SessionManager


def test_create_session():
    sm = SessionManager()
    session, msg = sm.create("dev-1", "1.2.3.4", "Chrome/120")
    assert session is not None
    assert session.session_id.startswith("sess_")
    assert msg == "Created"


def test_validate():
    sm = SessionManager()
    session, _ = sm.create("dev-2")
    valid, s = sm.validate(session.session_id)
    assert valid is True
    assert s is not None


def test_expired_session():
    sm = SessionManager(default_ttl=-1.0)
    session, _ = sm.create("dev-3")
    valid, _ = sm.validate(session.session_id)
    assert valid is False


def test_max_sessions():
    sm = SessionManager(max_sessions_per_user=2)
    sm.create("dev-4")
    sm.create("dev-4")
    session, msg = sm.create("dev-4")
    assert session is None
    assert "Max" in msg


def test_revoke():
    sm = SessionManager()
    session, _ = sm.create("dev-5")
    assert sm.revoke(session.session_id) is True
    valid, _ = sm.validate(session.session_id)
    assert valid is False


def test_revoke_all():
    sm = SessionManager()
    sm.create("dev-6")
    sm.create("dev-6")
    count = sm.revoke_all("dev-6")
    assert count == 2
    assert sm.get_active_sessions("dev-6") == []


def test_stats():
    sm = SessionManager()
    sm.create("dev-7")
    sm.create("dev-8")
    stats = sm.get_stats()
    assert stats["active"] == 2
    assert stats["unique_developers"] == 2
