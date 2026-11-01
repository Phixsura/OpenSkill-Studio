from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_satisfaction import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfaction, SatisfactionSignals,
)

class TestConsumerSatisfaction:
    def test_delighted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfaction()
        svc.update_signals("inst-1", SatisfactionSignals(consumer_id="c1", api_reliability_pct=99.9, avg_latency_ms=30, documentation_rating=5.0, nps_score=80))
        s = svc.compute("inst-1", "c1")
        assert s.sentiment == "delighted"

    def test_dissatisfied(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfaction()
        svc.update_signals("inst-1", SatisfactionSignals(consumer_id="c1", api_reliability_pct=90, avg_latency_ms=2000, support_resolution_hours=72, documentation_rating=1.0, nps_score=-80))
        s = svc.compute("inst-1", "c1")
        assert s.sentiment == "dissatisfied"

    def test_unknown_neutral(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfaction()
        s = svc.compute("inst-1", "unknown")
        assert s.sentiment == "neutral"

    def test_average(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfaction()
        svc.update_signals("inst-1", SatisfactionSignals(consumer_id="c1", api_reliability_pct=99, nps_score=50))
        svc.update_signals("inst-1", SatisfactionSignals(consumer_id="c2", api_reliability_pct=99, nps_score=50))
        assert svc.average_satisfaction("inst-1") > 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerSatisfaction()
        svc.update_signals("inst-1", SatisfactionSignals(consumer_id="c1"))
        assert len(svc.list_scores("inst-2")) == 0
