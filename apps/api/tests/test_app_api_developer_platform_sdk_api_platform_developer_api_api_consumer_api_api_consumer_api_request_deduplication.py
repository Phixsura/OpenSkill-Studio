import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_deduplication import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication,
)

class TestRequestDeduplication:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication()
        result = svc.check("inst-1", "c1", "key-1", self._now())
        assert not result.is_duplicate

    def test_duplicate_detected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication()
        svc.record("inst-1", "c1", "key-1", "hash1", 200, "body1", self._now())
        result = svc.check("inst-1", "c1", "key-1", self._now() + timedelta(minutes=5))
        assert result.is_duplicate and result.original_status == 200

    def test_expired_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication(ttl_hours=1)
        svc.record("inst-1", "c1", "key-1", "hash1", 200, "body1", self._now())
        result = svc.check("inst-1", "c1", "key-1", self._now() + timedelta(hours=2))
        assert not result.is_duplicate

    def test_cleanup(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication(ttl_hours=1)
        svc.record("inst-1", "c1", "key-1", "h", 200, "b", self._now())
        svc.record("inst-1", "c1", "key-2", "h", 200, "b", self._now())
        removed = svc.cleanup(self._now() + timedelta(hours=2))
        assert removed == 2

    def test_hash_request(self):
        h1 = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication.hash_request("POST", "/api/orders", '{"item":"a"}')
        h2 = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication.hash_request("POST", "/api/orders", '{"item":"b"}')
        assert h1 != h2 and len(h1) == 16

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplication()
        svc.record("inst-1", "c1", "key-1", "h", 200, "b", self._now())
        result = svc.check("inst-2", "c1", "key-1", self._now())
        assert not result.is_duplicate
