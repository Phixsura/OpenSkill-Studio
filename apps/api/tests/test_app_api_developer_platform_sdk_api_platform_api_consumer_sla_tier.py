import pytest
from app.services.app_api_developer_platform_sdk_api_platform_api_consumer_sla_tier import AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier

class TestConsumerSLATier:
    def test_assign(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier()
        c = s.assign("inst-1", "c1", "platinum")
        assert c.uptime_target == 99.99
        assert c.latency_target_ms == 100

    def test_invalid_tier(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier()
        with pytest.raises(ValueError):
            s.assign("inst-1", "c1", "diamond")

    def test_meeting_sla(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier()
        s.assign("inst-1", "c1", "gold")
        s.update_actuals("inst-1", "c1", 99.95, 150)
        assert s.all_consumers("inst-1")[0].meeting_sla is True

    def test_breaching(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier()
        s.assign("inst-1", "c1", "platinum")
        s.update_actuals("inst-1", "c1", 99.5, 500)
        assert len(s.breaching("inst-1")) == 1

    def test_by_tier(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier()
        s.assign("inst-1", "c1", "gold")
        s.assign("inst-1", "c2", "gold")
        s.assign("inst-1", "c3", "silver")
        assert s.by_tier("inst-1") == {"gold": 2, "silver": 1}

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSLATier()
        s.assign("inst-1", "c1", "gold")
        assert len(s.all_consumers("inst-2")) == 0
