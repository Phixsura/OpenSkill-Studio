import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_custom_domain import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomain, CustomDomain, DomainStatus,
)

class TestCustomDomain:
    def test_add_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomain()
        svc.add_domain("inst-1", CustomDomain(domain_id="d1", consumer_id="c1", domain="api.example.com"))
        d = svc.verify_domain("inst-1", "d1")
        assert d.status == DomainStatus.VERIFIED

    def test_activate_requires_verified(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomain()
        svc.add_domain("inst-1", CustomDomain(domain_id="d1", consumer_id="c1", domain="api.test.com"))
        with pytest.raises(ValueError, match="verified"):
            svc.activate("inst-1", "d1")

    def test_duplicate_domain(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomain()
        svc.add_domain("inst-1", CustomDomain(domain_id="d1", consumer_id="c1", domain="api.example.com"))
        with pytest.raises(ValueError, match="already registered"):
            svc.add_domain("inst-1", CustomDomain(domain_id="d2", consumer_id="c2", domain="api.example.com"))

    def test_invalid_domain(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomain()
        with pytest.raises(ValueError, match="Invalid domain"):
            svc.add_domain("inst-1", CustomDomain(domain_id="d1", consumer_id="c1", domain="not a domain"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCustomDomain()
        svc.add_domain("inst-1", CustomDomain(domain_id="d1", consumer_id="c1", domain="api.test.com"))
        assert len(svc.list_domains("inst-2")) == 0
