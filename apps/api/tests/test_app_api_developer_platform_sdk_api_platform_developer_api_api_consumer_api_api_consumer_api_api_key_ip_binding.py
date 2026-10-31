import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_api_key_ip_binding import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding, IpBinding,
)

class TestApiKeyIpBinding:
    def test_allowed_ip(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding()
        svc.bind("inst-1", IpBinding(key_id="k1", consumer_id="c1", allowed_ips=["10.0.0.0/24"]))
        assert svc.check("inst-1", "k1", "10.0.0.5") is True

    def test_blocked_ip(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding()
        svc.bind("inst-1", IpBinding(key_id="k1", consumer_id="c1", allowed_ips=["10.0.0.0/24"]))
        assert svc.check("inst-1", "k1", "192.168.1.1") is False

    def test_no_binding_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding()
        assert svc.check("inst-1", "k1", "1.2.3.4") is True

    def test_invalid_cidr(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding()
        with pytest.raises(ValueError, match="Invalid"):
            svc.bind("inst-1", IpBinding(key_id="k1", consumer_id="c1", allowed_ips=["not-an-ip"]))

    def test_violation_tracking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding()
        svc.bind("inst-1", IpBinding(key_id="k1", consumer_id="c1", allowed_ips=["10.0.0.0/8"]))
        svc.check("inst-1", "k1", "192.168.1.1")
        assert svc.get_binding("inst-1", "k1").violations == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiKeyIpBinding()
        svc.bind("inst-1", IpBinding(key_id="k1", consumer_id="c1", allowed_ips=["10.0.0.0/8"]))
        assert len(svc.list_bindings("inst-2")) == 0
