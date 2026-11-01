import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_health_check_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiHealthCheckConfig, HealthCheckConfig,
)

class TestConsumerApiHealthCheckConfig:
    def test_configure(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiHealthCheckConfig()
        cfg = svc.configure("inst-1", HealthCheckConfig(consumer_id="c1", check_interval_s=60, timeout_ms=3000))
        assert cfg.check_interval_s == 60

    def test_invalid_interval(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiHealthCheckConfig()
        with pytest.raises(ValueError, match="interval"):
            svc.configure("inst-1", HealthCheckConfig(consumer_id="c1", check_interval_s=2))

    def test_update_interval(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiHealthCheckConfig()
        svc.configure("inst-1", HealthCheckConfig(consumer_id="c1"))
        cfg = svc.update_interval("inst-1", "c1", 120)
        assert cfg.check_interval_s == 120

    def test_get_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiHealthCheckConfig()
        svc.configure("inst-1", HealthCheckConfig(consumer_id="c1", check_path="/status"))
        cfg = svc.get_config("inst-1", "c1")
        assert cfg is not None and cfg.check_path == "/status"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiHealthCheckConfig()
        svc.configure("inst-1", HealthCheckConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
