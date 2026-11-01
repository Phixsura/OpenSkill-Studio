import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_ip_allowlist import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist, IPEntry,
)

class TestConsumerApiIpAllowlist:
    def test_allowed_ip(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist()
        svc.add_entry("inst-1", "c1", IPEntry(entry_id="e1", cidr="10.0.0.0/24", label="Office"))
        result = svc.check("inst-1", "c1", "10.0.0.50")
        assert result.allowed and result.reason == "allowed"

    def test_blocked_ip(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist()
        svc.add_entry("inst-1", "c1", IPEntry(entry_id="e1", cidr="10.0.0.0/24"))
        result = svc.check("inst-1", "c1", "192.168.1.1")
        assert not result.allowed and result.reason == "not_in_allowlist"

    def test_no_allowlist_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist()
        result = svc.check("inst-1", "c1", "1.2.3.4")
        assert result.allowed and result.reason == "no_allowlist"

    def test_invalid_cidr(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist()
        with pytest.raises(ValueError, match="Invalid CIDR"):
            svc.add_entry("inst-1", "c1", IPEntry(entry_id="e1", cidr="not_a_cidr"))

    def test_duplicate_cidr(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist()
        svc.add_entry("inst-1", "c1", IPEntry(entry_id="e1", cidr="10.0.0.0/24"))
        with pytest.raises(ValueError, match="already in allowlist"):
            svc.add_entry("inst-1", "c1", IPEntry(entry_id="e2", cidr="10.0.0.0/24"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlist()
        svc.add_entry("inst-1", "c1", IPEntry(entry_id="e1", cidr="10.0.0.0/8"))
        result = svc.check("inst-2", "c1", "10.0.0.1")
        assert result.allowed and result.reason == "no_allowlist"
