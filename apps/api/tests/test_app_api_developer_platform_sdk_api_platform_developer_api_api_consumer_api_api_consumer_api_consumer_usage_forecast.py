import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_usage_forecast import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecast, UsageDataPoint,
)

class TestConsumerUsageForecast:
    def test_increasing_trend(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecast()
        for i, period in enumerate(["2026-01", "2026-02", "2026-03", "2026-04"]):
            svc.add_data("inst-1", "c1", UsageDataPoint(period=period, requests=1000 + i * 500))
        result = svc.forecast("inst-1", "c1", "2026-05")
        assert result.trend == "increasing" and result.predicted_requests > 2500

    def test_stable_trend(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecast()
        for period in ["2026-01", "2026-02", "2026-03"]:
            svc.add_data("inst-1", "c1", UsageDataPoint(period=period, requests=1000))
        result = svc.forecast("inst-1", "c1", "2026-04")
        assert result.trend == "stable"

    def test_single_point(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecast()
        svc.add_data("inst-1", "c1", UsageDataPoint(period="2026-01", requests=500))
        result = svc.forecast("inst-1", "c1", "2026-02")
        assert result.predicted_requests == 500 and result.confidence == 0.3

    def test_no_negative_prediction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecast()
        svc.add_data("inst-1", "c1", UsageDataPoint(period="2026-01", requests=100))
        svc.add_data("inst-1", "c1", UsageDataPoint(period="2026-02", requests=10))
        svc.add_data("inst-1", "c1", UsageDataPoint(period="2026-03", requests=1))
        result = svc.forecast("inst-1", "c1", "2026-04")
        assert result.predicted_requests >= 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerUsageForecast()
        svc.add_data("inst-1", "c1", UsageDataPoint(period="2026-01", requests=100))
        assert len(svc.get_history("inst-2", "c1")) == 0
