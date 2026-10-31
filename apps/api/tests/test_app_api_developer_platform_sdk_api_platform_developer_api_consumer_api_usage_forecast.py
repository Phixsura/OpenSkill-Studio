import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_api_usage_forecast import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerApiUsageForecast, UsageSample,
)

class TestConsumerApiUsageForecast:
    def test_growing_forecast(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerApiUsageForecast()
        samples = [UsageSample(f"2024-0{i}", 1000 * i) for i in range(1, 7)]
        svc.add_samples("inst-1", "c1", samples)
        f = svc.forecast("inst-1", "c1", "2024-07")
        assert f.trend == "growing"
        assert f.predicted_requests > 0
        assert f.confidence == "high"

    def test_stable_forecast(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerApiUsageForecast()
        samples = [UsageSample(f"2024-0{i}", 1000) for i in range(1, 7)]
        svc.add_samples("inst-1", "c1", samples)
        f = svc.forecast("inst-1", "c1", "2024-07")
        assert f.trend == "stable"

    def test_insufficient_data(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerApiUsageForecast()
        svc.add_samples("inst-1", "c1", [UsageSample("2024-01", 1000)])
        with pytest.raises(ValueError, match="at least 2"):
            svc.forecast("inst-1", "c1", "2024-02")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerApiUsageForecast()
        svc.add_samples("inst-1", "c1", [UsageSample("2024-01", 100), UsageSample("2024-02", 200)])
        assert svc.consumer_count("inst-2") == 0
