"""Tests for App SSO Provider — configure, auth tracking, toggle."""

import pytest

from app.services.app_sso_provider import AppSSOProvider


class TestConfigure:
    def test_configure(self):
        s = AppSSOProvider()
        p = s.configure("inst-1", "okta", "oidc", "Okta", "https://okta.com/issuer", "client-123")
        assert p.provider_type == "oidc"
        assert p.enabled is True

    def test_invalid_type(self):
        s = AppSSOProvider()
        with pytest.raises(ValueError):
            s.configure("inst-1", "p1", "ldap", "LDAP", "ldap://")


class TestAuth:
    def test_success_rate(self):
        s = AppSSOProvider()
        s.configure("inst-1", "okta", "oidc", "Okta", "https://okta.com")
        for _ in range(9):
            s.record_auth("inst-1", "okta", True)
        s.record_auth("inst-1", "okta", False)
        p = s.list_providers("inst-1")[0]
        assert p.success_rate == 90.0


class TestToggle:
    def test_disable(self):
        s = AppSSOProvider()
        s.configure("inst-1", "okta", "oidc", "Okta", "https://okta.com")
        s.toggle("inst-1", "okta", False)
        assert s.enabled_providers("inst-1") == []


class TestIsolation:
    def test_cross(self):
        s = AppSSOProvider()
        s.configure("inst-1", "okta", "oidc", "Okta", "https://okta.com")
        assert s.list_providers("inst-2") == []
