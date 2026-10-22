"""Advanced tests for idempotency, rate limiting, and SSRF protection."""

from app.services.idempotency import get_cached_response, make_key, store_response
from app.services.app_rate_limit import (
    RATE_LIMITS,
    check_rate_limit,
    cleanup_old_counters,
    get_app_usage,
    get_installation_usage,
    get_rate_limit_headers,
    record_request,
)
from app.services.event_dispatch import _is_safe_url


# ── Idempotency ──────────────────────────────────────────


def test_idempotency_store_retrieve():
    k = make_key("idem-adv-1", "POST", "/test")
    store_response(k, {"result": "cached"}, 200)
    cached = get_cached_response(k)
    assert cached == {"result": "cached"}


def test_idempotency_miss():
    k = make_key("nonexistent-client", "POST", "/path")
    assert get_cached_response(k) is None


def test_idempotency_key_isolation():
    k1 = make_key("c1", "POST", "/a")
    k2 = make_key("c1", "POST", "/b")
    k3 = make_key("c2", "POST", "/a")
    store_response(k1, {"v": 1})
    assert get_cached_response(k2) is None
    assert get_cached_response(k3) is None


def test_idempotency_key_deterministic():
    k1 = make_key("same", "POST", "/path")
    k2 = make_key("same", "POST", "/path")
    assert k1 == k2


# ── Rate Limiting ────────────────────────────────────────


def test_record_and_check():
    app_id = "rl-adv-app"
    record_request(app_id)
    record_request(app_id)
    usage = get_app_usage(app_id)
    assert usage["requests"] >= 2
    assert check_rate_limit(app_id, "standard") is True


def test_unlimited_always_passes():
    assert check_rate_limit("any-app", "unlimited") is True


def test_rate_limit_headers_standard():
    headers = get_rate_limit_headers("rl-hdr-app", "standard")
    assert headers["X-RateLimit-Limit"] == "1000"
    assert "X-RateLimit-Remaining" in headers
    assert "X-RateLimit-Reset" in headers


def test_rate_limit_headers_unlimited():
    headers = get_rate_limit_headers("rl-hdr-app2", "unlimited")
    assert headers["X-RateLimit-Limit"] == "unlimited"


def test_installation_usage():
    record_request("rl-inst-app", "rl-inst-1")
    usage = get_installation_usage("rl-inst-1")
    assert usage["requests"] >= 1


def test_cleanup_keeps_current():
    record_request("rl-clean-app")
    cleanup_old_counters()
    assert get_app_usage("rl-clean-app")["requests"] >= 1


def test_rate_limit_tiers_defined():
    assert RATE_LIMITS["standard"] == 1000
    assert RATE_LIMITS["elevated"] == 5000
    assert RATE_LIMITS["unlimited"] == 0


# ── SSRF Protection ──────────────────────────────────────


def test_ssrf_blocks_localhost():
    assert _is_safe_url("https://localhost") is False


def test_ssrf_blocks_metadata():
    assert _is_safe_url("https://169.254.169.254") is False


def test_ssrf_blocks_internal():
    assert _is_safe_url("https://metadata.google.internal") is False


def test_ssrf_blocks_http():
    assert _is_safe_url("http://example.com") is False


def test_ssrf_blocks_empty():
    assert _is_safe_url("") is False


def test_ssrf_blocks_malformed():
    assert _is_safe_url("not-a-url") is False
    assert _is_safe_url("ftp://example.com") is False
