"""Tests for Consumer API Token Exchange service."""
from app.services.app_api_developer_platform_sdk_consumer_api_token_exchange import (
    TokenExchange, ExchangeRequest,
)


class TestTokenExchange:
    def test_exchange_success(self):
        svc = TokenExchange()
        svc.register_token("tok-123", "c1", ["read", "write"])
        svc.add_trusted_audience("service-b")
        result = svc.exchange(ExchangeRequest("tok-123", "access_token", "service-b"))
        assert "access_token" in result
        assert result["token_type"] == "Bearer"
        assert result["audience"] == "service-b"

    def test_invalid_token(self):
        svc = TokenExchange()
        result = svc.exchange(ExchangeRequest("bad-token", "access_token", "svc"))
        assert result["error"] == "invalid_token"

    def test_untrusted_audience(self):
        svc = TokenExchange()
        svc.register_token("tok-123", "c1")
        svc.add_trusted_audience("only-this")
        result = svc.exchange(ExchangeRequest("tok-123", "access_token", "other"))
        assert result["error"] == "invalid_target"

    def test_no_audience_restriction(self):
        svc = TokenExchange()
        svc.register_token("tok-123", "c1")
        result = svc.exchange(ExchangeRequest("tok-123", "access_token", "any-service"))
        assert "access_token" in result

    def test_insufficient_scope(self):
        svc = TokenExchange()
        svc.register_token("tok-123", "c1", ["read"])
        result = svc.exchange(ExchangeRequest("tok-123", "access_token", "svc", scope="write"))
        assert result["error"] == "insufficient_scope"

    def test_scope_subset(self):
        svc = TokenExchange()
        svc.register_token("tok-123", "c1", ["read", "write", "admin"])
        result = svc.exchange(ExchangeRequest("tok-123", "access_token", "svc", scope="read write"))
        assert "access_token" in result
        assert result["scope"] == "read write"

    def test_unsupported_grant_type(self):
        svc = TokenExchange()
        result = svc.exchange(ExchangeRequest("tok", "jwt", "svc", grant_type="magic"))
        assert result["error"] == "unsupported_grant_type"

    def test_exchanged_token_is_valid(self):
        svc = TokenExchange()
        svc.register_token("tok-123", "c1", ["read"])
        r1 = svc.exchange(ExchangeRequest("tok-123", "access_token", "svc"))
        # The new token should also be usable for exchange
        r2 = svc.exchange(ExchangeRequest(r1["access_token"], "access_token", "svc"))
        assert "access_token" in r2

    def test_stats(self):
        svc = TokenExchange()
        svc.register_token("tok-123", "c1", ["read"])
        svc.add_trusted_audience("svc-a")
        svc.exchange(ExchangeRequest("tok-123", "access_token", "svc-a"))
        stats = svc.get_stats()
        assert stats["issued_exchanges"] == 1
        assert stats["trusted_audiences"] == 1

    def test_isolation(self):
        a, b = TokenExchange(), TokenExchange()
        a.register_token("tok", "c1")
        assert b.exchange(ExchangeRequest("tok", "access_token", "svc"))["error"] == "invalid_token"
