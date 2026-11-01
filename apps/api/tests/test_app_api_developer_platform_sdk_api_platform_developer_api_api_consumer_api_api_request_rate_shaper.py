from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_rate_shaper import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaper, RateShaperConfig,
)

class TestRequestRateShaper:
    def test_allows_under_target(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaper()
        svc.configure("inst-1", RateShaperConfig(consumer_id="c1", target_rps=100, smoothing_window_s=1))
        d = svc.shape("inst-1", "c1")
        assert d.allowed is True

    def test_shapes_over_burst(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaper()
        svc.configure("inst-1", RateShaperConfig(consumer_id="c1", target_rps=5, burst_tolerance=1.0, smoothing_window_s=1))
        for _ in range(5): svc.shape("inst-1", "c1")
        d = svc.shape("inst-1", "c1")
        assert d.allowed is False and d.delay_ms > 0

    def test_no_config_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaper()
        assert svc.shape("inst-1", "c1").allowed is True

    def test_invalid_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaper()
        import pytest
        with pytest.raises(ValueError):
            svc.configure("inst-1", RateShaperConfig(consumer_id="c1", target_rps=0))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRateShaper()
        svc.configure("inst-1", RateShaperConfig(consumer_id="c1", target_rps=10))
        assert len(svc.list_configs("inst-2")) == 0
