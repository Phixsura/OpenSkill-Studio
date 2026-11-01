"""App quota management tests."""

import pytest
from app.services.app_quota import get_limits, check_quota, TIER_LIMITS, QuotaLimits

def test_default_limits():
    l = get_limits()
    assert l.max_apps == 10

TIERS = list(TIER_LIMITS.keys())

@pytest.mark.parametrize("tier", TIERS)
def test_tier_limits(tier):
    l = get_limits(tier)
    assert isinstance(l, QuotaLimits)
    assert l.max_apps > 0

def test_free_lower_than_standard():
    assert get_limits("free").max_apps < get_limits("standard").max_apps

def test_premium_higher_than_standard():
    assert get_limits("premium").max_apps > get_limits("standard").max_apps

def test_enterprise_highest():
    assert get_limits("enterprise").max_apps >= get_limits("premium").max_apps

def test_check_quota_allowed():
    r = check_quota(current=3, limit=10, resource="apps")
    assert r["allowed"] is True
    assert r["remaining"] == 7

def test_check_quota_denied():
    r = check_quota(current=10, limit=10, resource="apps")
    assert r["allowed"] is False
    assert r["remaining"] == 0

def test_unknown_tier_defaults():
    l = get_limits("nonexistent")
    assert l == get_limits("standard")
