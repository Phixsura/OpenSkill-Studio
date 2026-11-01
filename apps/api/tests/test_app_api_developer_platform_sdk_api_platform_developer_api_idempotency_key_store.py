import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_idempotency_key_store import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStore

class TestIdempotencyKeyStore:
    def test_store_and_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStore(ttl_seconds=3600)
        svc.store("inst-1", "key-1", "POST", "/api/orders", 201, '{"id": "o1"}')
        rec = svc.check("inst-1", "key-1")
        assert rec is not None
        assert rec.response_status == 201

    def test_miss(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStore()
        assert svc.check("inst-1", "nope") is None

    def test_body_truncation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStore()
        big = "x" * 10000
        rec = svc.store("inst-1", "k1", "POST", "/api", 200, big)
        assert len(rec.response_body) < 10000
        assert rec.response_body.endswith("[TRUNCATED]")

    def test_delete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStore()
        svc.store("inst-1", "k1", "POST", "/api", 200, "ok")
        assert svc.delete("inst-1", "k1") is True
        assert svc.check("inst-1", "k1") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStore()
        svc.store("inst-1", "k1", "POST", "/api", 200, "ok")
        assert svc.check("inst-2", "k1") is None
        assert svc.count("inst-2") == 0
