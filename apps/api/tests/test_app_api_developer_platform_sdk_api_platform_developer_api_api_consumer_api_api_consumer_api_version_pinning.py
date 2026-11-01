from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_version_pinning import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinning

class TestConsumerApiVersionPinning:
    def test_pin_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinning()
        svc.pin("inst-1", "c1", "v2.0", reason="Compatibility")
        assert svc.get_version("inst-1", "c1") == "v2.0"

    def test_default_latest(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinning()
        assert svc.get_version("inst-1", "c1") == "latest"

    def test_unpin(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinning()
        svc.pin("inst-1", "c1", "v1.0")
        assert svc.unpin("inst-1", "c1") is True
        assert svc.get_version("inst-1", "c1") == "latest"

    def test_pinned_by_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinning()
        svc.pin("inst-1", "c1", "v1.0")
        svc.pin("inst-1", "c2", "v2.0")
        assert len(svc.pinned_consumers("inst-1", "v1.0")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinning()
        svc.pin("inst-1", "c1", "v1.0")
        assert len(svc.list_pins("inst-2")) == 0
