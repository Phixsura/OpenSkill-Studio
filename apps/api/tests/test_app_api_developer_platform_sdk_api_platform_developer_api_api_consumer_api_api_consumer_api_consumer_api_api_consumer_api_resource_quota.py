import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_resource_quota import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota, ResourceQuota,
)

class TestConsumerApiResourceQuota:
    def test_within_quota(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota()
        svc.set_quota("inst-1", ResourceQuota(resource_type="webhooks", consumer_id="c1", max_count=10))
        result = svc.consume("inst-1", "c1", "webhooks")
        assert result.allowed and result.current == 1 and result.remaining == 9

    def test_quota_exceeded(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota()
        svc.set_quota("inst-1", ResourceQuota(resource_type="api_keys", consumer_id="c1", max_count=2))
        svc.consume("inst-1", "c1", "api_keys")
        svc.consume("inst-1", "c1", "api_keys")
        result = svc.consume("inst-1", "c1", "api_keys")
        assert not result.allowed

    def test_release(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota()
        svc.set_quota("inst-1", ResourceQuota(resource_type="webhooks", consumer_id="c1", max_count=1))
        svc.consume("inst-1", "c1", "webhooks")
        svc.release("inst-1", "c1", "webhooks")
        result = svc.consume("inst-1", "c1", "webhooks")
        assert result.allowed

    def test_check_without_consume(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota()
        svc.set_quota("inst-1", ResourceQuota(resource_type="endpoints", consumer_id="c1", max_count=50, current_count=30))
        result = svc.check("inst-1", "c1", "endpoints")
        assert result.remaining == 20

    def test_invalid_resource(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota()
        with pytest.raises(ValueError, match="Invalid resource_type"):
            svc.set_quota("inst-1", ResourceQuota(resource_type="unknown", consumer_id="c1", max_count=10))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiResourceQuota()
        svc.set_quota("inst-1", ResourceQuota(resource_type="webhooks", consumer_id="c1", max_count=5))
        assert len(svc.list_quotas("inst-2", "c1")) == 0
