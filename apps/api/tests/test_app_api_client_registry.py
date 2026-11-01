"""Tests for App API Client Registry — register, status, activity."""

import pytest

from app.services.app_api_client_registry import AppAPIClientRegistry, ClientStatus


class TestRegister:
    def test_register(self):
        r = AppAPIClientRegistry()
        c = r.register("inst-1", "c1", "My App", "dev@example.com")
        assert c.status == ClientStatus.ACTIVE

    def test_duplicate(self):
        r = AppAPIClientRegistry()
        r.register("inst-1", "c1", "A", "a@b.com")
        with pytest.raises(ValueError, match="already registered"):
            r.register("inst-1", "c1", "B", "b@c.com")

    def test_invalid_email(self):
        r = AppAPIClientRegistry()
        with pytest.raises(ValueError, match="email"):
            r.register("inst-1", "c1", "App", "not-email")


class TestStatus:
    def test_suspend_reactivate(self):
        r = AppAPIClientRegistry()
        r.register("inst-1", "c1", "App", "a@b.com")
        r.suspend("inst-1", "c1")
        assert r.active_clients("inst-1") == []
        r.reactivate("inst-1", "c1")
        assert len(r.active_clients("inst-1")) == 1

    def test_revoke_no_reactivate(self):
        r = AppAPIClientRegistry()
        r.register("inst-1", "c1", "App", "a@b.com")
        r.revoke("inst-1", "c1")
        with pytest.raises(ValueError, match="revoked"):
            r.reactivate("inst-1", "c1")


class TestIsolation:
    def test_cross(self):
        r = AppAPIClientRegistry()
        r.register("inst-1", "c1", "App", "a@b.com")
        assert r.list_clients("inst-2") == []
