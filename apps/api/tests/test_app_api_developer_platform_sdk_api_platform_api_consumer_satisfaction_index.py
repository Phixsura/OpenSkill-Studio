from app.services.app_api_developer_platform_sdk_api_platform_api_consumer_satisfaction_index import AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndex

class TestConsumerSatisfactionIndex:
    def test_delighted(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndex()
        idx = s.update("inst-1", "c1", api_reliability_score=95, latency_score=90, documentation_score=85, support_score=90, overall_nps=80)
        assert idx.satisfaction_tier == "delighted"

    def test_dissatisfied(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndex()
        idx = s.update("inst-1", "c1", api_reliability_score=30, latency_score=20, documentation_score=10, support_score=15, overall_nps=-50)
        assert idx.satisfaction_tier == "dissatisfied"

    def test_avg_csi(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndex()
        s.update("inst-1", "c1", api_reliability_score=90, latency_score=90, documentation_score=90, support_score=90, overall_nps=80)
        s.update("inst-1", "c2", api_reliability_score=50, latency_score=50, documentation_score=50, support_score=50, overall_nps=0)
        assert s.avg_csi("inst-1") > 0

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerSatisfactionIndex()
        s.update("inst-1", "c1", api_reliability_score=90)
        assert s.avg_csi("inst-2") == 0.0
