"""Tests for OAuth Token Introspection — RFC 7662, scopes, revocation, caching."""

import time

import pytest

from app.services.oauth_token_introspection import (
    CACHE_TTL_SECONDS,
    OAuthTokenIntrospector,
    TokenType,
    hash_token,
)


class TestHashToken:
    def test_deterministic(self):
        assert hash_token("abc") == hash_token("abc")

    def test_different_tokens_differ(self):
        assert hash_token("token-a") != hash_token("token-b")

    def test_hex_64_chars(self):
        assert len(hash_token("anything")) == 64


class TestRegisterAndIntrospect:
    def test_active_token(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="user-1",
                             scope="read:skills write:skills")
        resp = intro.introspect("tok-1")
        assert resp.active is True
        assert resp.client_id == "app-1"
        assert resp.sub == "user-1"
        assert resp.scope == "read:skills write:skills"
        assert resp.token_type == "access_token"
        assert resp.iss == "https://openskill.io"

    def test_unknown_token_inactive(self):
        intro = OAuthTokenIntrospector()
        resp = intro.introspect("nonexistent-token")
        assert resp.active is False
        assert resp.scope is None

    def test_expired_token_inactive(self):
        intro = OAuthTokenIntrospector()
        now = time.time()
        intro.register_token("tok-1", client_id="app-1", user_id="user-1",
                             scope="read:skills", ttl_seconds=60)
        # Introspect after expiry
        resp = intro.introspect("tok-1", now=now + 120)
        assert resp.active is False

    def test_exp_and_iat_set(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id=None,
                             scope="read:skills", ttl_seconds=3600)
        resp = intro.introspect("tok-1")
        assert resp.exp is not None
        assert resp.iat is not None
        assert resp.exp > resp.iat

    def test_refresh_token_type(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1",
                             scope="offline_access", token_type=TokenType.REFRESH)
        resp = intro.introspect("tok-1")
        assert resp.token_type == "refresh_token"


class TestRevocation:
    def test_revoked_token_inactive(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1", scope="read:skills")
        assert intro.introspect("tok-1").active is True
        revoked = intro.revoke_token("tok-1")
        assert revoked is True
        assert intro.introspect("tok-1").active is False

    def test_revoke_unknown_returns_false(self):
        intro = OAuthTokenIntrospector()
        assert intro.revoke_token("nonexistent") is False

    def test_revoke_invalidates_cache(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1", scope="read:skills")
        # Populate cache
        intro.introspect("tok-1")
        # Revoke
        intro.revoke_token("tok-1")
        # Should be inactive immediately (cache invalidated)
        assert intro.introspect("tok-1").active is False


class TestScopeChecking:
    def test_has_scope(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1",
                             scope="read:skills write:projects read:email")
        assert intro.has_scope("tok-1", "read:skills") is True
        assert intro.has_scope("tok-1", "write:projects") is True
        assert intro.has_scope("tok-1", "admin:org") is False

    def test_has_scope_inactive_token(self):
        intro = OAuthTokenIntrospector()
        assert intro.has_scope("nonexistent", "read:skills") is False

    def test_has_all_scopes(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1",
                             scope="read:skills write:projects")
        assert intro.has_all_scopes("tok-1", ["read:skills", "write:projects"]) is True
        assert intro.has_all_scopes("tok-1", ["read:skills", "admin:org"]) is False

    def test_has_any_scope(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1",
                             scope="read:skills")
        assert intro.has_any_scope("tok-1", ["read:skills", "admin:org"]) is True
        assert intro.has_any_scope("tok-1", ["admin:org", "write:billing"]) is False


class TestCaching:
    def test_cache_hit(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1", scope="read:skills")
        now = time.time()
        intro.introspect("tok-1", now=now)
        intro.introspect("tok-1", now=now + 1)
        assert intro.cache_hit_rate > 0

    def test_cache_expires(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1", scope="read:skills")
        now = time.time()
        intro.introspect("tok-1", now=now)
        # After TTL, should re-compute
        intro.introspect("tok-1", now=now + CACHE_TTL_SECONDS + 1)
        # 2 introspections, at most 0 cache hits (first was fresh, second was expired)
        assert intro.total_introspections == 2


class TestToDict:
    def test_active_response_dict(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("tok-1", client_id="app-1", user_id="u1", scope="read:skills")
        resp = intro.introspect("tok-1")
        d = resp.to_dict()
        assert d["active"] is True
        assert d["scope"] == "read:skills"
        assert d["client_id"] == "app-1"
        assert "exp" in d
        assert "iat" in d

    def test_inactive_response_dict(self):
        intro = OAuthTokenIntrospector()
        d = intro.introspect("unknown").to_dict()
        assert d == {"active": False}

    def test_no_none_fields(self):
        intro = OAuthTokenIntrospector()
        d = intro.introspect("unknown").to_dict()
        assert None not in d.values()


class TestStats:
    def test_active_token_count(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("t1", client_id="a1", user_id="u1", scope="s")
        intro.register_token("t2", client_id="a2", user_id="u2", scope="s")
        assert intro.active_token_count == 2
        intro.revoke_token("t1")
        assert intro.active_token_count == 1

    def test_total_introspections(self):
        intro = OAuthTokenIntrospector()
        intro.register_token("t1", client_id="a1", user_id="u1", scope="s")
        intro.introspect("t1")
        intro.introspect("t1")
        intro.introspect("t1")
        assert intro.total_introspections == 3
