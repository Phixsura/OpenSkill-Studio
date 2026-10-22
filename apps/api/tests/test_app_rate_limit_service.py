"""App rate limit service tests."""

import pytest
from app.services.app_rate_limit import (
    record_request, get_app_usage, get_installation_usage,
    check_rate_limit, get_rate_limit_headers, cleanup_old_counters,
)

TIERS = ["standard", "premium", "enterprise"]

def test_record_and_get_usage():
    app_id = "test-rl-001"
    record_request(app_id)
    usage = get_app_usage(app_id)
    assert isinstance(usage, dict)

def test_installation_usage():
    record_request("test-rl-002", installation_id="inst-001")
    usage = get_installation_usage("inst-001")
    assert isinstance(usage, dict)

@pytest.mark.parametrize("tier", TIERS)
def test_check_rate_limit_tiers(tier):
    result = check_rate_limit("test-rl-tier", tier=tier)
    assert isinstance(result, bool)

@pytest.mark.parametrize("tier", TIERS)
def test_rate_limit_headers(tier):
    headers = get_rate_limit_headers("test-rl-hdr", tier=tier)
    assert isinstance(headers, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in headers.items())

def test_rate_limit_headers_keys():
    headers = get_rate_limit_headers("test-rl-keys")
    expected_keys = {"X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"}
    assert expected_keys.issubset(set(headers.keys()))

def test_cleanup():
    removed = cleanup_old_counters()
    assert isinstance(removed, int)
    assert removed >= 0

def test_fresh_app_under_limit():
    assert check_rate_limit("brand-new-app-never-used") is True
