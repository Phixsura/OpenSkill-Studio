"""Rate limit tier hierarchy — premium > standard, enterprise > premium."""

import pytest
from app.services.app_rate_limit import check_rate_limit, record_request, get_rate_limit_headers

def test_tier_limits_increase():
    """Higher tiers should have higher limits."""
    standard = int(get_rate_limit_headers("tier-cmp", tier="standard")["X-RateLimit-Limit"])
    premium = int(get_rate_limit_headers("tier-cmp", tier="premium")["X-RateLimit-Limit"])
    enterprise = int(get_rate_limit_headers("tier-cmp", tier="enterprise")["X-RateLimit-Limit"])
    assert premium >= standard
    assert enterprise >= premium

def test_standard_limit_reasonable():
    headers = get_rate_limit_headers("std-check", tier="standard")
    limit = int(headers["X-RateLimit-Limit"])
    assert 100 <= limit <= 100000

def test_reset_header_is_numeric():
    headers = get_rate_limit_headers("reset-check")
    assert headers["X-RateLimit-Reset"].isdigit()

def test_remaining_decreases():
    app = "remaining-dec-test"
    h1 = int(get_rate_limit_headers(app)["X-RateLimit-Remaining"])
    record_request(app)
    h2 = int(get_rate_limit_headers(app)["X-RateLimit-Remaining"])
    assert h2 < h1
