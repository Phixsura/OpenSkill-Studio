import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_request_throttle import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestThrottle

class TestApiRequestThrottle:
    def test_acquire_and_release(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestThrottle()
        svc.configure("inst-1", "c1", max_concurrent=2)
        r1 = svc.acquire("inst-1", "c1")
        assert r1["allowed"] is True and r1["active"] == 1
        r2 = svc.acquire("inst-1", "c1")
        assert r2["allowed"] is True and r2["active"] == 2
        r3 = svc.acquire("inst-1", "c1")
        assert r3["allowed"] is False
        svc.release("inst-1", "c1")
        r4 = svc.acquire("inst-1", "c1")
        assert r4["allowed"] is True

    def test_no_config_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestThrottle()
        assert svc.acquire("inst-1", "c1")["allowed"] is True

    def test_throttle_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestThrottle()
        svc.configure("inst-1", "c1", max_concurrent=1)
        svc.acquire("inst-1", "c1")  # served
        svc.acquire("inst-1", "c1")  # throttled
        assert svc.throttle_rate("inst-1", "c1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestThrottle()
        svc.configure("inst-1", "c1", max_concurrent=5)
        assert len(svc.list_configs("inst-2")) == 0
