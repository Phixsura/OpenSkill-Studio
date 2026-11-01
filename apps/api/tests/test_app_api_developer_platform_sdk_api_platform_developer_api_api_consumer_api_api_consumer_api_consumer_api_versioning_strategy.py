import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_versioning_strategy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy, APIVersion, VersionStrategy,
)

class TestConsumerApiVersioningStrategy:
    def test_path_resolution(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy()
        svc.register_version("inst-1", APIVersion(version="v1"))
        svc.register_version("inst-1", APIVersion(version="v2"))
        svc.set_strategy("inst-1", VersionStrategy(strategy_type="path", default_version="v1"))
        result = svc.resolve("inst-1", "c1", path_version="v2")
        assert result.resolved_version == "v2" and result.source == "path"

    def test_default_fallback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy()
        svc.register_version("inst-1", APIVersion(version="v1"))
        svc.set_strategy("inst-1", VersionStrategy(default_version="v1"))
        result = svc.resolve("inst-1", "c1")
        assert result.resolved_version == "v1" and result.source == "default"

    def test_pinned_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy()
        svc.register_version("inst-1", APIVersion(version="v1"))
        svc.register_version("inst-1", APIVersion(version="v2"))
        svc.pin_consumer("inst-1", "c1", "v1")
        result = svc.resolve("inst-1", "c1", path_version="v2")
        assert result.resolved_version == "v1" and result.source == "pinned"

    def test_deprecated_flag(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy()
        svc.register_version("inst-1", APIVersion(version="v1", status="deprecated"))
        svc.set_strategy("inst-1", VersionStrategy(default_version="v1"))
        result = svc.resolve("inst-1", "c1")
        assert result.deprecated

    def test_override_disabled(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy()
        svc.register_version("inst-1", APIVersion(version="v1"))
        svc.set_strategy("inst-1", VersionStrategy(default_version="v1", allow_version_override=False))
        result = svc.resolve("inst-1", "c1", path_version="v2")
        assert result.resolved_version == "v1" and result.source == "default"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategy()
        svc.register_version("inst-1", APIVersion(version="v1"))
        assert len(svc.list_versions("inst-2")) == 0
