import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_key_metadata import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata, APIKeyMeta,
)

class TestConsumerApiKeyMetadata:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata()
        svc.set_metadata("inst-1", APIKeyMeta(key_id="k1", consumer_id="c1", label="Main Key", environment="production"))
        meta = svc.get("inst-1", "c1", "k1")
        assert meta.label == "Main Key"

    def test_record_usage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata()
        svc.set_metadata("inst-1", APIKeyMeta(key_id="k1", consumer_id="c1"))
        svc.record_usage("inst-1", "c1", "k1", self._now())
        svc.record_usage("inst-1", "c1", "k1", self._now())
        meta = svc.get("inst-1", "c1", "k1")
        assert meta.request_count == 2

    def test_filter_by_env(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata()
        svc.set_metadata("inst-1", APIKeyMeta(key_id="k1", consumer_id="c1", environment="production"))
        svc.set_metadata("inst-1", APIKeyMeta(key_id="k2", consumer_id="c1", environment="staging"))
        assert len(svc.list_keys("inst-1", "c1", environment="production")) == 1

    def test_find_by_tag(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata()
        svc.set_metadata("inst-1", APIKeyMeta(key_id="k1", consumer_id="c1", tags={"team": "backend"}))
        svc.set_metadata("inst-1", APIKeyMeta(key_id="k2", consumer_id="c1", tags={"team": "frontend"}))
        found = svc.find_by_tag("inst-1", "c1", "team", "backend")
        assert len(found) == 1 and found[0].key_id == "k1"

    def test_invalid_env(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata()
        with pytest.raises(ValueError, match="Invalid environment"):
            svc.set_metadata("inst-1", APIKeyMeta(key_id="k1", consumer_id="c1", environment="testing"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata()
        svc.set_metadata("inst-1", APIKeyMeta(key_id="k1", consumer_id="c1"))
        assert svc.get("inst-2", "c1", "k1") is None
