import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_sdk_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig, SDKConfig,
)

class TestConsumerApiSdkConfig:
    def test_create_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig()
        svc.create("inst-1", SDKConfig(config_id="c1", consumer_id="con1", language="typescript", base_url="https://api.example.com"))
        cfg = svc.get("inst-1", "c1")
        assert cfg.language == "typescript"

    def test_snippet_typescript(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig()
        svc.create("inst-1", SDKConfig(config_id="c1", consumer_id="con1", language="typescript", base_url="https://api.ex.com"))
        snippet = svc.generate_snippet("inst-1", "c1")
        assert "APIClient" in snippet and "https://api.ex.com" in snippet

    def test_snippet_python(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig()
        svc.create("inst-1", SDKConfig(config_id="c1", consumer_id="con1", language="python", base_url="https://api.ex.com"))
        snippet = svc.generate_snippet("inst-1", "c1")
        assert "APIClient" in snippet and "base_url" in snippet

    def test_invalid_language(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig()
        with pytest.raises(ValueError, match="Unsupported language"):
            svc.create("inst-1", SDKConfig(config_id="c1", consumer_id="con1", language="cobol"))

    def test_invalid_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig()
        with pytest.raises(ValueError, match="timeout_ms"):
            svc.create("inst-1", SDKConfig(config_id="c1", consumer_id="con1", language="python", timeout_ms=100))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig()
        svc.create("inst-1", SDKConfig(config_id="c1", consumer_id="con1", language="go"))
        assert svc.get("inst-2", "c1") is None
