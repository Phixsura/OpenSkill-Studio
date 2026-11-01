"""Tests for App Rate Limit Policy — endpoint matching, burst, exemptions."""

import pytest

from app.services.app_rate_limit_policy import AppRateLimitPolicy


class TestAddRule:
    def test_add_and_list(self):
        p = AppRateLimitPolicy()
        r = p.add_rule("app-1", "GET", "/api/v1/skills", 100)
        assert r.rule_id is not None
        assert len(p.get_rules("app-1")) == 1

    def test_negative_rate_rejected(self):
        p = AppRateLimitPolicy()
        with pytest.raises(ValueError):
            p.add_rule("app-1", "GET", "/api/v1/skills", -1)

    def test_remove_rule(self):
        p = AppRateLimitPolicy()
        r = p.add_rule("app-1", "GET", "/api/v1/skills", 100)
        assert p.remove_rule("app-1", r.rule_id) is True
        assert len(p.get_rules("app-1")) == 0

    def test_remove_nonexistent(self):
        p = AppRateLimitPolicy()
        assert p.remove_rule("app-1", "fake") is False


class TestExactMatch:
    def test_exact_path(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills", 60)
        d = p.evaluate("app-1", "GET", "/api/v1/skills")
        assert d.matched_rule is not None
        assert d.limit == 60

    def test_wrong_method(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills", 60)
        d = p.evaluate("app-1", "POST", "/api/v1/skills")
        assert d.matched_rule is None

    def test_wrong_path(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills", 60)
        d = p.evaluate("app-1", "GET", "/api/v1/projects")
        assert d.matched_rule is None


class TestWildcard:
    def test_wildcard_method(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "*", "/api/v1/skills", 120)
        d = p.evaluate("app-1", "POST", "/api/v1/skills")
        assert d.matched_rule is not None

    def test_wildcard_path(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/*", 200)
        d = p.evaluate("app-1", "GET", "/api/v1/skills")
        assert d.matched_rule is not None
        assert d.limit == 200

    def test_trailing_slash_wildcard(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills/*", 50)
        d = p.evaluate("app-1", "GET", "/api/v1/skills/123")
        assert d.matched_rule is not None

    def test_exact_prefix_without_slash(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills/*", 50)
        d = p.evaluate("app-1", "GET", "/api/v1/skills")
        assert d.matched_rule is not None


class TestBurst:
    def test_burst_in_decision(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "POST", "/api/v1/submit", 30, burst_size=10)
        d = p.evaluate("app-1", "POST", "/api/v1/submit")
        assert d.burst == 10


class TestExemption:
    def test_exempt_endpoint(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/health", 0, exempt=True)
        d = p.evaluate("app-1", "GET", "/api/v1/health")
        assert d.exempt is True
        assert d.limit == 0

    def test_non_exempt(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills", 100)
        d = p.evaluate("app-1", "GET", "/api/v1/skills")
        assert d.exempt is False


class TestHeaders:
    def test_headers_set(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills", 100, burst_size=20)
        d = p.evaluate("app-1", "GET", "/api/v1/skills")
        assert d.headers["X-RateLimit-Limit"] == "100"
        assert d.headers["X-RateLimit-Burst"] == "20"

    def test_no_headers_when_no_match(self):
        p = AppRateLimitPolicy()
        d = p.evaluate("app-1", "GET", "/unknown")
        assert d.headers == {}

    def test_no_headers_when_exempt(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/health", 0, exempt=True)
        d = p.evaluate("app-1", "GET", "/health")
        assert d.headers == {}


class TestPriority:
    def test_first_match_wins(self):
        p = AppRateLimitPolicy()
        p.add_rule("app-1", "GET", "/api/v1/skills/*", 50)  # specific
        p.add_rule("app-1", "GET", "/api/v1/*", 200)          # broad
        d = p.evaluate("app-1", "GET", "/api/v1/skills/123")
        assert d.limit == 50  # first rule wins
