from app.services.app_marketplace_extension_token_introspect import TokenIntrospectorService
import time


def test_issue_and_introspect():
    ti = TokenIntrospectorService()
    record = ti.issue("user-1", "app-1", ["read", "write"])
    result = ti.introspect(record.token)
    assert result["active"] is True
    assert result["sub"] == "user-1"
    assert result["scope"] == "read write"
    assert result["token_type"] == "access_token"


def test_expired_token():
    ti = TokenIntrospectorService()
    record = ti.issue("user-1", "app-1", ["read"], ttl_seconds=0.01)
    time.sleep(0.02)
    result = ti.introspect(record.token)
    assert result["active"] is False


def test_revoked_token():
    ti = TokenIntrospectorService()
    record = ti.issue("user-1", "app-1", ["read"])
    ti.revoke(record.token)
    result = ti.introspect(record.token)
    assert result["active"] is False


def test_unknown_token():
    ti = TokenIntrospectorService()
    result = ti.introspect("nonexistent-token")
    assert result == {"active": False}


def test_client_binding():
    ti = TokenIntrospectorService()
    record = ti.issue("user-1", "app-1", ["read"])
    # Same client can introspect
    assert ti.introspect(record.token, "app-1")["active"] is True
    # Different client cannot
    assert ti.introspect(record.token, "app-2")["active"] is False


def test_revoke_wrong_client():
    ti = TokenIntrospectorService()
    record = ti.issue("user-1", "app-1", ["read"])
    assert ti.revoke(record.token, "app-2") is False  # wrong client
    assert ti.introspect(record.token)["active"] is True  # still active


def test_revoke_by_subject():
    ti = TokenIntrospectorService()
    t1 = ti.issue("user-1", "app-1", ["read"])
    t2 = ti.issue("user-1", "app-2", ["write"])
    t3 = ti.issue("user-2", "app-1", ["read"])
    count = ti.revoke_by_subject("user-1")
    assert count == 2
    assert ti.introspect(t1.token)["active"] is False
    assert ti.introspect(t3.token)["active"] is True


def test_refresh_token():
    ti = TokenIntrospectorService()
    record = ti.issue("user-1", "app-1", ["offline_access"],
                      token_type="refresh_token", ttl_seconds=86400 * 30)
    result = ti.introspect(record.token)
    assert result["token_type"] == "refresh_token"


def test_cleanup():
    ti = TokenIntrospectorService()
    ti.issue("u", "a", [], ttl_seconds=0.01)
    time.sleep(0.02)
    ti.issue("u", "a", [])
    ti.revoke(ti.issue("u", "a", []).token)
    before = ti.stats()["total"]
    # cleanup needs 24h buffer for expired, but revoked cleaned immediately
    cleaned = ti.cleanup_expired()
    assert cleaned >= 1


def test_stats():
    ti = TokenIntrospectorService()
    ti.issue("u1", "a", [], ttl_seconds=60)
    ti.issue("u2", "a", [], ttl_seconds=60)
    stats = ti.stats()
    assert stats["active"] == 2
