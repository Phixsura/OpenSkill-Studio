from app.services.app_marketplace_token_introspection import TokenIntrospectionService


def test_register_and_introspect():
    tis = TokenIntrospectionService()
    tis.register_token("tok_abc123", "client-1", "user-1", ["read", "write"])
    result = tis.introspect("tok_abc123")
    assert result["active"] is True
    assert result["client_id"] == "client-1"
    assert result["sub"] == "user-1"
    assert "read" in result["scope"]


def test_unknown_token():
    tis = TokenIntrospectionService()
    result = tis.introspect("unknown_token")
    assert result["active"] is False


def test_expired_token():
    tis = TokenIntrospectionService()
    tis.register_token("tok_expired", "c1", "u1", ["read"], ttl_seconds=-1)
    result = tis.introspect("tok_expired")
    assert result["active"] is False
    assert result.get("reason") == "expired"


def test_revoke():
    tis = TokenIntrospectionService()
    tis.register_token("tok_revoke", "c2", "u2", ["read"])
    assert tis.revoke("tok_revoke") is True
    result = tis.introspect("tok_revoke")
    assert result["active"] is False
    assert result.get("reason") == "revoked"


def test_has_scope():
    tis = TokenIntrospectionService()
    tis.register_token("tok_scoped", "c3", "u3", ["read", "analytics"])
    assert tis.has_scope("tok_scoped", "read") is True
    assert tis.has_scope("tok_scoped", "admin") is False


def test_wildcard_scope():
    tis = TokenIntrospectionService()
    tis.register_token("tok_wild", "c4", "u4", ["*"])
    assert tis.has_scope("tok_wild", "anything") is True


def test_active_count():
    tis = TokenIntrospectionService()
    tis.register_token("t1", "c5", "u1", ["r"])
    tis.register_token("t2", "c5", "u2", ["r"])
    tis.register_token("t3", "c6", "u3", ["r"])
    assert tis.get_active_count("c5") == 2
    assert tis.get_active_count() == 3
