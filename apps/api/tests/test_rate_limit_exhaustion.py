"""Rate limit exhaustion tests."""

import pytest
from app.services.app_rate_limit import record_request, check_rate_limit, get_rate_limit_headers

def test_standard_tier_exhaustion():
    """Exhaust the standard tier limit and verify denial."""
    app_id = "exhaust-test-standard"
    # Record enough requests to potentially exceed
    for _ in range(1001):
        record_request(app_id)
    result = check_rate_limit(app_id, tier="standard")
    # Should be denied after exceeding limit
    assert result is False

def test_premium_tier_higher_limit():
    """Premium tier should allow more requests than standard."""
    app_id = "exhaust-test-premium"
    for _ in range(1001):
        record_request(app_id)
    # Premium may still allow
    premium = check_rate_limit(app_id, tier="premium")
    standard = check_rate_limit(app_id, tier="standard")
    # premium should be >= standard (at least as permissive)
    assert premium >= standard

def test_headers_reflect_usage():
    app_id = "header-reflect-test"
    record_request(app_id)
    headers = get_rate_limit_headers(app_id)
    remaining = int(headers["X-RateLimit-Remaining"])
    limit = int(headers["X-RateLimit-Limit"])
    assert remaining < limit
