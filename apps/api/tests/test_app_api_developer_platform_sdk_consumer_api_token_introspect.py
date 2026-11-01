"""Tests for API Token Introspection service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_token_introspect import TokenIntrospection


class TestTokenIntrospection:
    def test_issue_and_introspect(self):
        svc = TokenIntrospection()
        issued = svc.issue("c1", "access", ["read"], issued_at=100.0, ttl_seconds=3600)
        result = svc.introspect(issued["token"], current_time=200.0)
        assert result["active"] is True
        assert result["consumer_id"] == "c1"
        assert result["scopes"] == ["read"]

    def test_expired_token(self):
        svc = TokenIntrospection()
        issued = svc.issue("c1", "access", issued_at=100.0, ttl_seconds=60)
        result = svc.introspect(issued["token"], current_time=200.0)
        assert result["active"] is False
        assert result["reason"] == "expired"

    def test_revoke(self):
        svc = TokenIntrospection()
        issued = svc.issue("c1", "access", issued_at=0.0)
        svc.revoke(issued["token_id"])
        result = svc.introspect(issued["token"], current_time=0.0)
        assert result["active"] is False
        assert result["reason"] == "revoked"

    def test_revoke_all(self):
        svc = TokenIntrospection()
        svc.issue("c1", "access", issued_at=0.0)
        svc.issue("c1", "refresh", issued_at=0.0)
        svc.issue("c2", "access", issued_at=0.0)
        result = svc.revoke_all("c1")
        assert result["revoked_count"] == 2

    def test_unknown_token(self):
        svc = TokenIntrospection()
        result = svc.introspect("fake-token")
        assert result["active"] is False

    def test_remaining_seconds(self):
        svc = TokenIntrospection()
        issued = svc.issue("c1", "access", issued_at=100.0, ttl_seconds=3600)
        result = svc.introspect(issued["token"], current_time=200.0)
        assert result["remaining_seconds"] == 3500.0

    def test_list_tokens(self):
        svc = TokenIntrospection()
        svc.issue("c1", "access", issued_at=0.0)
        svc.issue("c1", "api_key", issued_at=0.0)
        tokens = svc.list_tokens("c1")
        assert len(tokens) == 2

    def test_stats(self):
        svc = TokenIntrospection()
        issued = svc.issue("c1", "access", issued_at=0.0)
        svc.issue("c1", "refresh", issued_at=0.0)
        svc.revoke(issued["token_id"])
        stats = svc.get_stats()
        assert stats["total_tokens"] == 2
        assert stats["revoked"] == 1
        assert stats["by_type"]["access"] == 1

    def test_invalid_type(self):
        svc = TokenIntrospection()
        with pytest.raises(ValueError):
            svc.issue("c1", "bearer")

    def test_isolation(self):
        a, b = TokenIntrospection(), TokenIntrospection()
        issued = a.issue("c1", "access", issued_at=0.0)
        assert b.introspect(issued["token"])["active"] is False
