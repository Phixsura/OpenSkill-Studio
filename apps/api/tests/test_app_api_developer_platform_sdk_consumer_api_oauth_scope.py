"""Tests for Consumer OAuth Scope Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_oauth_scope import (
    OAuthScopeManager, Scope,
)


class TestOAuthScopeManager:
    def _setup(self):
        svc = OAuthScopeManager()
        svc.register_scope(Scope("read:users", "Read Users", category="users"))
        svc.register_scope(Scope("write:users", "Write Users", category="users", sensitive=True))
        svc.register_scope(Scope("read:orders", "Read Orders", category="orders"))
        svc.register_scope(Scope("admin", "Admin Access", sensitive=True))
        return svc

    def test_grant_and_check(self):
        svc = self._setup()
        svc.grant("c1", ["read:users", "read:orders"])
        result = svc.check("c1", ["read:users"])
        assert result["allowed"] is True

    def test_check_missing(self):
        svc = self._setup()
        svc.grant("c1", ["read:users"])
        result = svc.check("c1", ["write:users"])
        assert result["allowed"] is False
        assert "write:users" in result["missing"]

    def test_no_grants(self):
        svc = self._setup()
        result = svc.check("unknown", ["read:users"])
        assert result["allowed"] is False

    def test_revoke(self):
        svc = self._setup()
        svc.grant("c1", ["read:users", "read:orders"])
        svc.revoke("c1", ["read:users"])
        result = svc.check("c1", ["read:users"])
        assert result["allowed"] is False

    def test_dependency_auto_grant(self):
        svc = self._setup()
        svc.add_dependency("write:users", "read:users")
        svc.grant("c1", ["write:users"])
        result = svc.check("c1", ["read:users"])
        assert result["allowed"] is True

    def test_consumer_scopes(self):
        svc = self._setup()
        svc.grant("c1", ["read:users", "admin"])
        scopes = svc.get_consumer_scopes("c1")
        assert len(scopes) == 2
        sensitive = [s for s in scopes if s["sensitive"]]
        assert len(sensitive) == 1

    def test_list_by_category(self):
        svc = self._setup()
        user_scopes = svc.list_scopes(category="users")
        assert len(user_scopes) == 2

    def test_self_dependency_rejected(self):
        svc = self._setup()
        with pytest.raises(ValueError):
            svc.add_dependency("read:users", "read:users")

    def test_unknown_scope(self):
        svc = self._setup()
        with pytest.raises(ValueError):
            svc.grant("c1", ["nonexistent"])

    def test_stats(self):
        svc = self._setup()
        svc.grant("c1", ["read:users"])
        stats = svc.get_stats()
        assert stats["total_scopes"] == 4
        assert stats["sensitive_scopes"] == 2
        assert stats["consumers_with_grants"] == 1

    def test_isolation(self):
        a = self._setup()
        b = OAuthScopeManager()
        a.grant("c1", ["read:users"])
        assert b.check("c1", ["read:users"])["allowed"] is False
