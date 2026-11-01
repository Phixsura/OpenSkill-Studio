from app.services.app_marketplace_extension_rate_limit_policy import (
    RateLimitPolicyService, Algorithm,
)
import pytest


def test_sliding_window_allows():
    svc = RateLimitPolicyService()
    svc.create_policy("ext-1", "/api/data", Algorithm.SLIDING_WINDOW, 10, 60)
    r = svc.check("ext-1", "/api/data", "user-1")
    assert r.allowed is True
    assert r.remaining == 9


def test_sliding_window_blocks():
    svc = RateLimitPolicyService()
    svc.create_policy("ext-1", "/api/data", Algorithm.SLIDING_WINDOW, 3, 60)
    for _ in range(3):
        svc.check("ext-1", "/api/data", "user-1")
    r = svc.check("ext-1", "/api/data", "user-1")
    assert r.allowed is False
    assert r.remaining == 0
    assert r.retry_after > 0


def test_token_bucket_allows():
    svc = RateLimitPolicyService()
    svc.create_policy("ext-1", "/api/query", Algorithm.TOKEN_BUCKET, 100, 60, burst_size=5)
    r = svc.check("ext-1", "/api/query", "user-1")
    assert r.allowed is True
    assert r.remaining == 4  # burst_size - 1


def test_token_bucket_exhaustion():
    svc = RateLimitPolicyService()
    svc.create_policy("ext-1", "/api/query", Algorithm.TOKEN_BUCKET, 100, 60, burst_size=2)
    svc.check("ext-1", "/api/query", "u1")
    svc.check("ext-1", "/api/query", "u1")
    r = svc.check("ext-1", "/api/query", "u1")
    assert r.allowed is False


def test_headers():
    svc = RateLimitPolicyService()
    svc.create_policy("ext-1", "/api/data", Algorithm.SLIDING_WINDOW, 100, 60)
    r = svc.check("ext-1", "/api/data")
    headers = r.headers
    assert "X-RateLimit-Limit" in headers
    assert headers["X-RateLimit-Limit"] == "100"
    assert "Retry-After" not in headers  # allowed


def test_no_policy_allows():
    svc = RateLimitPolicyService()
    r = svc.check("ext-x", "/unknown")
    assert r.allowed is True


def test_per_user_isolation():
    svc = RateLimitPolicyService()
    svc.create_policy("ext-1", "/api", Algorithm.SLIDING_WINDOW, 2, 60)
    svc.check("ext-1", "/api", "user-1")
    svc.check("ext-1", "/api", "user-1")
    r1 = svc.check("ext-1", "/api", "user-1")
    r2 = svc.check("ext-1", "/api", "user-2")
    assert r1.allowed is False
    assert r2.allowed is True


def test_invalid_config():
    svc = RateLimitPolicyService()
    with pytest.raises(ValueError):
        svc.create_policy("ext-1", "/api", Algorithm.SLIDING_WINDOW, 0, 60)
