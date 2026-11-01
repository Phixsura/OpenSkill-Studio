from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_usage_heatmap import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageHeatmap

class TestUsageHeatmap:
    def test_record_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageHeatmap()
        svc.record("inst-1", "mon", 9, 100)
        svc.record("inst-1", "mon", 9, 50)
        hm = svc.get_heatmap("inst-1")
        assert len(hm) == 1 and hm[0].request_count == 150

    def test_peak_hour(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageHeatmap()
        svc.record("inst-1", "tue", 14, 500)
        svc.record("inst-1", "wed", 10, 200)
        peak = svc.peak_hour("inst-1")
        assert peak == ("tue", 14, 500)

    def test_invalid_day(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageHeatmap()
        import pytest
        with pytest.raises(ValueError):
            svc.record("inst-1", "xyz", 10)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageHeatmap()
        svc.record("inst-1", "mon", 9, 100)
        assert svc.total_requests("inst-2") == 0
