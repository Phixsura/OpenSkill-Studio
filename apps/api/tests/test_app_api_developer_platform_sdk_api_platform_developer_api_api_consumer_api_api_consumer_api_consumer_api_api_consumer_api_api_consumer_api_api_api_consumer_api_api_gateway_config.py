import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_gateway_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig, GatewayConfig,
)

class TestConsumerApiGatewayConfig:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig()
        svc.set_config("inst-1", GatewayConfig(consumer_id="c1", timeout_ms=5000, compression_enabled=True))
        cfg = svc.get_config("inst-1", "c1")
        assert cfg.timeout_ms == 5000 and cfg.compression_enabled

    def test_default_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig()
        cfg = svc.get_config("inst-1", "missing")
        assert cfg.timeout_ms == 30000

    def test_blocked_path(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig()
        svc.set_config("inst-1", GatewayConfig(consumer_id="c1", blocked_paths=["/api/admin", "/internal"]))
        assert svc.is_path_blocked("inst-1", "c1", "/api/admin/users")
        assert not svc.is_path_blocked("inst-1", "c1", "/api/users")

    def test_merge_headers_skips_forbidden(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig()
        svc.set_config("inst-1", GatewayConfig(consumer_id="c1", custom_headers={"X-Custom": "val", "Host": "evil.com"}))
        merged = svc.merge_headers("inst-1", "c1", {"Accept": "application/json"})
        assert merged["X-Custom"] == "val" and merged.get("Host") != "evil.com"

    def test_invalid_log_level(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig()
        with pytest.raises(ValueError, match="Invalid logging_level"):
            svc.set_config("inst-1", GatewayConfig(consumer_id="c1", logging_level="verbose"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiGatewayConfig()
        svc.set_config("inst-1", GatewayConfig(consumer_id="c1", timeout_ms=5000))
        assert svc.get_config("inst-2", "c1").timeout_ms == 30000  # default
