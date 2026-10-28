"""Tests for App Custom Domain — add, verify, SSL, ready check."""

import pytest

from app.services.app_custom_domain import AppCustomDomain, DomainStatus, SSLStatus


class TestAdd:
    def test_add(self):
        d = AppCustomDomain()
        dom = d.add_domain("inst-1", "d1", "api.example.com", "app-123.internal")
        assert dom.hostname == "api.example.com"
        assert dom.dns_status == DomainStatus.PENDING

    def test_normalize(self):
        d = AppCustomDomain()
        dom = d.add_domain("inst-1", "d1", "  API.Example.COM.  ", "target")
        assert dom.hostname == "api.example.com"


class TestVerify:
    def test_dns_success(self):
        d = AppCustomDomain()
        d.add_domain("inst-1", "d1", "api.example.com", "target")
        dom = d.verify_dns("inst-1", "d1", True)
        assert dom.dns_status == DomainStatus.VERIFIED

    def test_dns_fail(self):
        d = AppCustomDomain()
        d.add_domain("inst-1", "d1", "api.example.com", "target")
        dom = d.verify_dns("inst-1", "d1", False)
        assert dom.dns_status == DomainStatus.FAILED


class TestSSL:
    def test_ssl_active(self):
        d = AppCustomDomain()
        d.add_domain("inst-1", "d1", "api.example.com", "target")
        dom = d.update_ssl("inst-1", "d1", SSLStatus.ACTIVE)
        assert dom.ssl_status == SSLStatus.ACTIVE


class TestReady:
    def test_ready(self):
        d = AppCustomDomain()
        d.add_domain("inst-1", "d1", "api.example.com", "target")
        d.verify_dns("inst-1", "d1", True)
        d.update_ssl("inst-1", "d1", SSLStatus.ACTIVE)
        assert len(d.ready_domains("inst-1")) == 1

    def test_not_ready(self):
        d = AppCustomDomain()
        d.add_domain("inst-1", "d1", "api.example.com", "target")
        assert len(d.ready_domains("inst-1")) == 0


class TestFind:
    def test_find_by_hostname(self):
        d = AppCustomDomain()
        d.add_domain("inst-1", "d1", "api.example.com", "target")
        dom = d.find_by_hostname("inst-1", "API.Example.COM")
        assert dom is not None


class TestIsolation:
    def test_cross(self):
        d = AppCustomDomain()
        d.add_domain("inst-1", "d1", "api.example.com", "target")
        assert d.list_domains("inst-2") == []
