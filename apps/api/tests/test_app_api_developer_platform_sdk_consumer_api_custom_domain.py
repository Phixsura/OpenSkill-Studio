"""Tests for Consumer Custom Domain service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_custom_domain import CustomDomainManager


class TestCustomDomainManager:
    def test_add_domain(self):
        svc = CustomDomainManager()
        result = svc.add_domain("c1", "api.example.com")
        assert result["cname_target"] == "c1.api.platform.io"

    def test_verify_dns(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.example.com")
        result = svc.verify_dns("api.example.com")
        assert result["dns_verified"] is True
        assert result["ssl_status"] == "provisioning"

    def test_provision_ssl(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.example.com")
        svc.verify_dns("api.example.com")
        result = svc.provision_ssl("api.example.com", success=True, expires_at="2025-12-31")
        assert result["ssl_status"] == "active"

    def test_ssl_without_dns(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.example.com")
        result = svc.provision_ssl("api.example.com")
        assert result["error"] == "dns_not_verified"

    def test_ssl_failure(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.example.com")
        svc.verify_dns("api.example.com")
        result = svc.provision_ssl("api.example.com", success=False)
        assert result["ssl_status"] == "failed"

    def test_remove_domain(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.example.com")
        assert svc.remove_domain("api.example.com")["removed"] is True
        assert svc.get_domain("api.example.com") is None

    def test_list_by_consumer(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.a.com")
        svc.add_domain("c1", "api.b.com")
        svc.add_domain("c2", "api.c.com")
        assert len(svc.list_domains(consumer_id="c1")) == 2

    def test_invalid_domain(self):
        svc = CustomDomainManager()
        with pytest.raises(ValueError):
            svc.add_domain("c1", "not a domain!")

    def test_duplicate_domain(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.example.com")
        with pytest.raises(ValueError):
            svc.add_domain("c2", "api.example.com")

    def test_stats(self):
        svc = CustomDomainManager()
        svc.add_domain("c1", "api.a.com")
        svc.add_domain("c1", "api.b.com")
        svc.verify_dns("api.a.com")
        svc.provision_ssl("api.a.com", success=True)
        stats = svc.get_stats()
        assert stats["total_domains"] == 2
        assert stats["ssl_active"] == 1
        assert stats["dns_verified"] == 1

    def test_isolation(self):
        a, b = CustomDomainManager(), CustomDomainManager()
        a.add_domain("c1", "api.test.com")
        assert b.get_domain("api.test.com") is None
