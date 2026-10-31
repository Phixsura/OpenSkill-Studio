from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_ip_reputation import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputation

class TestRequestIpReputation:
    def test_starts_trusted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputation()
        rep = svc.get_or_create("inst-1", "10.0.0.1")
        assert rep.score == 100 and rep.tier == "trusted"

    def test_degrade_on_suspicious(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputation()
        for _ in range(5): svc.record_request("inst-1", "10.0.0.1", suspicious=True)
        rep = svc.get_or_create("inst-1", "10.0.0.1")
        assert rep.score == 50 and rep.tier == "neutral"

    def test_block_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputation()
        for _ in range(10): svc.record_request("inst-1", "10.0.0.1", suspicious=True)
        assert svc.should_block("inst-1", "10.0.0.1") is True

    def test_suspicious_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputation()
        svc.record_request("inst-1", "10.0.0.1")  # good
        for _ in range(8): svc.record_request("inst-1", "10.0.0.2", suspicious=True)
        assert len(svc.suspicious_ips("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIpReputation()
        svc.get_or_create("inst-1", "10.0.0.1")
        assert len(svc.list_reputations("inst-2")) == 0
