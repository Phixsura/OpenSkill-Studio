from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_id_generator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGenerator, RequestIdConfig,
)

class TestRequestIdGenerator:
    def test_default_hex(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGenerator()
        rid = svc.generate("inst-1")
        assert rid.startswith("req-")

    def test_custom_prefix(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGenerator()
        svc.configure("inst-1", "c1", RequestIdConfig(prefix="api", format="hex", length=16))
        rid = svc.generate("inst-1", "c1")
        assert rid.startswith("api-")

    def test_unique(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGenerator()
        ids = {svc.generate("inst-1") for _ in range(100)}
        assert len(ids) == 100

    def test_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGenerator()
        for _ in range(5): svc.generate("inst-1")
        assert svc.total_generated("inst-1") == 5

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGenerator()
        svc.generate("inst-1")
        assert svc.total_generated("inst-2") == 0
