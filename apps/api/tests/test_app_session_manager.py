"""Tests for App Session Manager — create, validate, revoke."""

import pytest

from app.services.app_session_manager import AppSessionManager


class TestCreate:
    def test_create(self):
        m = AppSessionManager()
        session, token = m.create("inst-1", "user-1", ip_address="10.0.0.1")
        assert session.user_id == "user-1"
        assert session.is_active is True
        assert len(token) > 20


class TestValidate:
    def test_valid(self):
        m = AppSessionManager()
        _, token = m.create("inst-1", "user-1")
        s = m.validate("inst-1", token)
        assert s is not None
        assert s.user_id == "user-1"

    def test_invalid(self):
        m = AppSessionManager()
        m.create("inst-1", "user-1")
        assert m.validate("inst-1", "bad-token") is None

    def test_revoked(self):
        m = AppSessionManager()
        session, token = m.create("inst-1", "user-1")
        m.revoke("inst-1", session.session_id)
        assert m.validate("inst-1", token) is None


class TestRevoke:
    def test_revoke_single(self):
        m = AppSessionManager()
        session, _ = m.create("inst-1", "user-1")
        s = m.revoke("inst-1", session.session_id)
        assert s.revoked is True

    def test_revoke_all(self):
        m = AppSessionManager()
        m.create("inst-1", "user-1")
        m.create("inst-1", "user-1")
        m.create("inst-1", "user-2")
        count = m.revoke_all("inst-1", "user-1")
        assert count == 2
        assert len(m.active_sessions("inst-1", "user-1")) == 0
        assert len(m.active_sessions("inst-1", "user-2")) == 1


class TestIsolation:
    def test_cross(self):
        m = AppSessionManager()
        _, token = m.create("inst-1", "user-1")
        assert m.validate("inst-2", token) is None
