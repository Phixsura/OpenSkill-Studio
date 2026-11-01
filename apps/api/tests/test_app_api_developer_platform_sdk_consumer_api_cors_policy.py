"""Tests for Consumer CORS Policy service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_cors_policy import (
    CorsPolicyManager, CorsConfig,
)


class TestCorsPolicyManager:
    def test_set_and_check(self):
        svc = CorsPolicyManager()
        svc.set_policy(CorsConfig("c1", allowed_origins=["https://example.com"]))
        result = svc.check_origin("c1", "https://example.com")
        assert result["allowed"] is True

    def test_origin_not_allowed(self):
        svc = CorsPolicyManager()
        svc.set_policy(CorsConfig("c1", allowed_origins=["https://example.com"]))
        result = svc.check_origin("c1", "https://evil.com")
        assert result["allowed"] is False

    def test_wildcard_origin(self):
        svc = CorsPolicyManager()
        svc.set_policy(CorsConfig("c1", allowed_origins=["*"]))
        result = svc.check_origin("c1", "https://anything.com")
        assert result["allowed"] is True

    def test_credentials_with_wildcard_rejected(self):
        svc = CorsPolicyManager()
        with pytest.raises(ValueError):
            svc.set_policy(CorsConfig("c1", allowed_origins=["*"], allow_credentials=True))

    def test_get_headers(self):
        svc = CorsPolicyManager()
        svc.set_policy(CorsConfig("c1", allowed_origins=["https://app.com"],
                                   allowed_methods=["GET", "POST"],
                                   allow_credentials=True))
        headers = svc.get_headers("c1", "https://app.com")
        assert headers["Access-Control-Allow-Origin"] == "https://app.com"
        assert "GET" in headers["Access-Control-Allow-Methods"]
        assert headers["Access-Control-Allow-Credentials"] == "true"

    def test_no_headers_for_disallowed(self):
        svc = CorsPolicyManager()
        svc.set_policy(CorsConfig("c1", allowed_origins=["https://app.com"]))
        headers = svc.get_headers("c1", "https://evil.com")
        assert headers == {}

    def test_add_origin(self):
        svc = CorsPolicyManager()
        svc.set_policy(CorsConfig("c1", allowed_origins=["https://a.com"]))
        svc.add_origin("c1", "https://b.com")
        assert svc.check_origin("c1", "https://b.com")["allowed"] is True

    def test_remove_origin(self):
        svc = CorsPolicyManager()
        svc.set_policy(CorsConfig("c1", allowed_origins=["https://a.com", "https://b.com"]))
        svc.remove_origin("c1", "https://a.com")
        assert svc.check_origin("c1", "https://a.com")["allowed"] is False

    def test_invalid_origin(self):
        svc = CorsPolicyManager()
        with pytest.raises(ValueError):
            svc.set_policy(CorsConfig("c1", allowed_origins=["not-a-url"]))

    def test_invalid_method(self):
        svc = CorsPolicyManager()
        with pytest.raises(ValueError):
            svc.set_policy(CorsConfig("c1", allowed_origins=["*"], allowed_methods=["TRACE"]))

    def test_no_policy(self):
        svc = CorsPolicyManager()
        assert svc.check_origin("missing", "https://x.com")["reason"] == "no_policy"

    def test_isolation(self):
        a, b = CorsPolicyManager(), CorsPolicyManager()
        a.set_policy(CorsConfig("c1", allowed_origins=["*"]))
        assert b.check_origin("c1", "https://x.com")["allowed"] is False
