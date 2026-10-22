"""Parametrized rate limit tests."""

import pytest
from app.services.app_rate_limit import RATE_LIMITS, check_rate_limit, get_rate_limit_headers

TIERS = list(RATE_LIMITS.keys())

@pytest.mark.parametrize("tier", TIERS)
def test_check_fresh_app(tier):
    assert check_rate_limit(f"param-rl-{tier}", tier) is True

@pytest.mark.parametrize("tier", TIERS)
def test_headers_format(tier):
    headers = get_rate_limit_headers(f"param-hdr-{tier}", tier)
    assert "X-RateLimit-Limit" in headers
    assert "X-RateLimit-Remaining" in headers

@pytest.mark.parametrize("tier,expected", [("standard", "1000"), ("elevated", "5000"), ("unlimited", "unlimited")])
def test_tier_limits(tier, expected):
    headers = get_rate_limit_headers(f"param-lim-{tier}", tier)
    assert headers["X-RateLimit-Limit"] == expected
