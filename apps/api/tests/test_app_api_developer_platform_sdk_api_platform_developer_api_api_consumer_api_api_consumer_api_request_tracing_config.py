import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_tracing_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfig, TracingConfig,
)

class TestRequestTracingConfig:
    def test_configure(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfig()
        cfg = svc.configure("inst-1", TracingConfig(consumer_id="c1", sample_rate=0.5, propagation_format="b3"))
        assert cfg.sample_rate == 0.5

    def test_tracing_enabled(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfig()
        svc.configure("inst-1", TracingConfig(consumer_id="c1", enabled=True, sample_rate=1.0))
        assert svc.is_tracing_enabled("inst-1", "c1") is True

    def test_disabled_tracing(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfig()
        svc.configure("inst-1", TracingConfig(consumer_id="c1", enabled=False))
        assert svc.is_tracing_enabled("inst-1", "c1") is False

    def test_invalid_propagation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfig()
        with pytest.raises(ValueError, match="Invalid propagation"):
            svc.configure("inst-1", TracingConfig(consumer_id="c1", propagation_format="custom"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestTracingConfig()
        svc.configure("inst-1", TracingConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
