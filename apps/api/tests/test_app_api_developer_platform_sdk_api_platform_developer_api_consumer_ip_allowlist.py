import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_ip_allowlist import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist, IpEntry,
)

class TestConsumerIpAllowlist:
    def test_allow_listed_ip(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist()
        svc.add_entry("inst-1", "c1", IpEntry(entry_id="e1", network="10.0.0.0/24", label="Office"))
        assert svc.check_ip("inst-1", "c1", "10.0.0.5") is True
        assert svc.check_ip("inst-1", "c1", "192.168.1.1") is False

    def test_no_allowlist_allows_all(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist()
        assert svc.check_ip("inst-1", "c1", "1.2.3.4") is True

    def test_single_ip(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist()
        svc.add_entry("inst-1", "c1", IpEntry(entry_id="e1", network="203.0.113.50/32"))
        assert svc.check_ip("inst-1", "c1", "203.0.113.50") is True
        assert svc.check_ip("inst-1", "c1", "203.0.113.51") is False

    def test_invalid_network(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist()
        with pytest.raises(ValueError, match="Invalid network"):
            svc.add_entry("inst-1", "c1", IpEntry(entry_id="e1", network="not-an-ip"))

    def test_remove_entry(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist()
        svc.add_entry("inst-1", "c1", IpEntry(entry_id="e1", network="10.0.0.0/8"))
        assert svc.remove_entry("inst-1", "c1", "e1") is True
        assert len(svc.list_entries("inst-1", "c1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlist()
        svc.add_entry("inst-1", "c1", IpEntry(entry_id="e1", network="10.0.0.0/8"))
        assert svc.consumer_count("inst-2") == 0
