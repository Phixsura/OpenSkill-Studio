"""Tests for App Custom Domain Manager — registration, verification, SSL."""

import pytest

from app.services.app_custom_domain import AppCustomDomainManager, DomainStatus, SSLStatus


class TestRegister:
    def test_register(self):
        m = AppCustomDomainManager()
        d = m.register_domain("inst-1", "d1", "app.example.com")
        assert d.domain == "app.example.com"
        assert d.status == DomainStatus.PENDING
        assert d.verification_token != ""

    def test_invalid_domain(self):
        m = AppCustomDomainManager()
        with pytest.raises(ValueError, match="Invalid domain"):
            m.register_domain("inst-1", "d1", "not a domain!")

    def test_duplicate_id(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "a.example.com")
        with pytest.raises(ValueError, match="already exists"):
            m.register_domain("inst-1", "d1", "b.example.com")

    def test_duplicate_domain(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "app.example.com")
        with pytest.raises(ValueError, match="already registered"):
            m.register_domain("inst-2", "d2", "app.example.com")

    def test_lowercased(self):
        m = AppCustomDomainManager()
        d = m.register_domain("inst-1", "d1", "APP.Example.COM")
        assert d.domain == "app.example.com"


class TestVerification:
    def test_full_verification(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "app.example.com")
        m.start_verification("inst-1", "d1")
        d = m.complete_verification("inst-1", "d1", now=1000.0)
        assert d.status == DomainStatus.VERIFIED
        assert d.verified_at == 1000.0

    def test_fail_verification(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "app.example.com")
        m.start_verification("inst-1", "d1")
        d = m.fail_verification("inst-1", "d1")
        assert d.status == DomainStatus.FAILED

    def test_cannot_verify_verified(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "app.example.com")
        m.start_verification("inst-1", "d1")
        m.complete_verification("inst-1", "d1")
        with pytest.raises(ValueError):
            m.start_verification("inst-1", "d1")


class TestSSL:
    def test_update_ssl(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "app.example.com")
        d = m.update_ssl("inst-1", "d1", SSLStatus.ACTIVE)
        assert d.ssl_status == SSLStatus.ACTIVE


class TestRemove:
    def test_remove(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "app.example.com")
        assert m.remove_domain("inst-1", "d1") is True
        assert m.list_domains("inst-1") == []

    def test_remove_nonexistent(self):
        m = AppCustomDomainManager()
        assert m.remove_domain("inst-1", "nope") is False


class TestIsolation:
    def test_cross_installation(self):
        m = AppCustomDomainManager()
        m.register_domain("inst-1", "d1", "app.example.com")
        with pytest.raises(KeyError):
            m.get_domain("inst-2", "d1")
