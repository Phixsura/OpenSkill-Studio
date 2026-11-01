"""Tests for App Session Store — create, token lookup, revoke, expiry."""

import pytest

from app.services.app_session_store import AppSessionStore


class TestCreateSession:
    def test_create(self):
        s = AppSessionStore()
        sess = s.create_session("inst-1", "s1", "user-1", now=1000.0)
        assert sess.session_id == "s1"
        assert sess.user_id == "user-1"
        assert len(sess.token) > 20
        assert sess.revoked is False

    def test_with_data(self):
        s = AppSessionStore()
        sess = s.create_session("inst-1", "s1", "user-1", data={"role": "admin"})
        assert sess.data["role"] == "admin"

    def test_duplicate(self):
        s = AppSessionStore()
        s.create_session("inst-1", "s1", "user-1")
        with pytest.raises(ValueError, match="already exists"):
            s.create_session("inst-1", "s1", "user-1")

    def test_missing_user_id(self):
        s = AppSessionStore()
        with pytest.raises(ValueError, match="user_id"):
            s.create_session("inst-1", "s1", "")


class TestGetByToken:
    def test_valid_token(self):
        s = AppSessionStore()
        sess = s.create_session("inst-1", "s1", "user-1", now=1000.0)
        found = s.get_by_token(sess.token, now=1000.0)
        assert found is not None
        assert found.session_id == "s1"

    def test_invalid_token(self):
        s = AppSessionStore()
        assert s.get_by_token("bogus") is None

    def test_expired_token(self):
        s = AppSessionStore(ttl_seconds=60)
        sess = s.create_session("inst-1", "s1", "user-1", now=1000.0)
        assert s.get_by_token(sess.token, now=1061.0) is None

    def test_revoked_token(self):
        s = AppSessionStore()
        sess = s.create_session("inst-1", "s1", "user-1", now=1000.0)
        s.revoke_session("inst-1", "s1")
        assert s.get_by_token(sess.token, now=1000.0) is None

    def test_updates_last_accessed(self):
        s = AppSessionStore()
        sess = s.create_session("inst-1", "s1", "user-1", now=1000.0)
        s.get_by_token(sess.token, now=1050.0)
        assert sess.last_accessed_at == 1050.0


class TestRevoke:
    def test_revoke(self):
        s = AppSessionStore()
        s.create_session("inst-1", "s1", "user-1")
        sess = s.revoke_session("inst-1", "s1")
        assert sess.revoked is True

    def test_revoke_user_sessions(self):
        s = AppSessionStore()
        s.create_session("inst-1", "s1", "user-1")
        s.create_session("inst-1", "s2", "user-1")
        s.create_session("inst-1", "s3", "user-2")
        count = s.revoke_user_sessions("inst-1", "user-1")
        assert count == 2


class TestUpdateData:
    def test_update(self):
        s = AppSessionStore()
        s.create_session("inst-1", "s1", "user-1", data={"a": 1})
        sess = s.update_data("inst-1", "s1", {"b": 2})
        assert sess.data == {"a": 1, "b": 2}

    def test_cannot_update_revoked(self):
        s = AppSessionStore()
        s.create_session("inst-1", "s1", "user-1")
        s.revoke_session("inst-1", "s1")
        with pytest.raises(ValueError, match="revoked"):
            s.update_data("inst-1", "s1", {"x": 1})


class TestListSessions:
    def test_active_only(self):
        s = AppSessionStore(ttl_seconds=3600)
        s.create_session("inst-1", "s1", "user-1", now=1000.0)
        s.create_session("inst-1", "s2", "user-1", now=1000.0)
        s.revoke_session("inst-1", "s2")
        sessions = s.list_user_sessions("inst-1", "user-1", now=1000.0)
        assert len(sessions) == 1

    def test_includes_all(self):
        s = AppSessionStore()
        s.create_session("inst-1", "s1", "user-1")
        s.create_session("inst-1", "s2", "user-1")
        s.revoke_session("inst-1", "s2")
        sessions = s.list_user_sessions("inst-1", "user-1", active_only=False)
        assert len(sessions) == 2


class TestCleanup:
    def test_cleanup_expired(self):
        s = AppSessionStore(ttl_seconds=60)
        s.create_session("inst-1", "s1", "user-1", now=1000.0)
        s.create_session("inst-1", "s2", "user-1", now=1000.0)
        count = s.cleanup_expired(now=1061.0)
        assert count == 2

    def test_cleanup_keeps_active(self):
        s = AppSessionStore(ttl_seconds=3600)
        s.create_session("inst-1", "s1", "user-1", now=1000.0)
        count = s.cleanup_expired(now=1001.0)
        assert count == 0


class TestIsolation:
    def test_cross_installation(self):
        s = AppSessionStore()
        s.create_session("inst-1", "s1", "user-1")
        with pytest.raises(KeyError):
            s.get_session("inst-2", "s1")


class TestConfig:
    def test_invalid_ttl(self):
        with pytest.raises(ValueError, match="ttl_seconds"):
            AppSessionStore(ttl_seconds=0)
