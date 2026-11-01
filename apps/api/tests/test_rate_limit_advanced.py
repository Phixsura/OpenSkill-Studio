"""Advanced rate limit tests."""

from app.services.app_rate_limit import (
    RATE_LIMITS,
    check_rate_limit,
    get_app_usage,
    get_installation_usage,
    get_rate_limit_headers,
    record_request,
)


def test_elevated_tier_limit():
    assert RATE_LIMITS["elevated"] == 5000


def test_record_multiple():
    for _ in range(5):
        record_request("rl-multi-app", "rl-multi-inst")
    assert get_app_usage("rl-multi-app")["requests"] >= 5
    assert get_installation_usage("rl-multi-inst")["requests"] >= 5


def test_headers_contain_all_fields():
    headers = get_rate_limit_headers("rl-hdr-full", "elevated")
    assert headers["X-RateLimit-Limit"] == "5000"
    assert int(headers["X-RateLimit-Remaining"]) <= 5000
    assert int(headers["X-RateLimit-Reset"]) > 0


def test_different_apps_independent():
    record_request("rl-indep-a")
    record_request("rl-indep-b")
    record_request("rl-indep-b")
    assert get_app_usage("rl-indep-a")["requests"] >= 1
    assert get_app_usage("rl-indep-b")["requests"] >= 2


def test_check_elevated():
    assert check_rate_limit("rl-elev-app", "elevated") is True


def test_unknown_tier_uses_standard():
    headers = get_rate_limit_headers("rl-unknown", "nonexistent_tier")
    assert headers["X-RateLimit-Limit"] == "1000"
