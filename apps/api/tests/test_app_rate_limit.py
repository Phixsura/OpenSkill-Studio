"""Tests for per-app rate limiting."""

from app.services.app_rate_limit import (
    check_rate_limit,
    cleanup_old_counters,
    get_app_usage,
    get_installation_usage,
    get_rate_limit_headers,
    record_request,
)


def test_record_and_get_usage():
    record_request("app-rl-1", "inst-rl-1")
    record_request("app-rl-1", "inst-rl-1")
    record_request("app-rl-1")

    usage = get_app_usage("app-rl-1")
    assert usage["requests"] == 3
    assert usage["app_id"] == "app-rl-1"

    inst_usage = get_installation_usage("inst-rl-1")
    assert inst_usage["requests"] == 2


def test_check_rate_limit_standard():
    # Fresh app should be under limit
    assert check_rate_limit("app-rl-fresh") is True


def test_check_rate_limit_unlimited():
    assert check_rate_limit("app-rl-any", "unlimited") is True


def test_rate_limit_headers():
    headers = get_rate_limit_headers("app-rl-headers", "standard")
    assert headers["X-RateLimit-Limit"] == "1000"
    assert int(headers["X-RateLimit-Remaining"]) <= 1000
    assert "X-RateLimit-Reset" in headers


def test_rate_limit_headers_unlimited():
    headers = get_rate_limit_headers("app-rl-unl", "unlimited")
    assert headers["X-RateLimit-Limit"] == "unlimited"


def test_cleanup():
    record_request("app-rl-cleanup")
    removed = cleanup_old_counters()
    # Current hour keys remain
    assert get_app_usage("app-rl-cleanup")["requests"] >= 1


def test_empty_app_usage():
    usage = get_app_usage("nonexistent-app")
    assert usage["requests"] == 0


def test_empty_install_usage():
    usage = get_installation_usage("nonexistent-inst")
    assert usage["requests"] == 0
