import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_connection_pool import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool, PoolConfig,
)

class TestConsumerApiConnectionPool:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_acquire_and_release(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool()
        svc.configure("inst-1", PoolConfig(consumer_id="c1", max_connections=5))
        conn = svc.acquire("inst-1", "c1", "conn-1", self._now())
        assert conn.state == "active"
        released = svc.release("inst-1", "c1", "conn-1", self._now())
        assert released.state == "idle"

    def test_pool_exhausted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool()
        svc.configure("inst-1", PoolConfig(consumer_id="c1", max_connections=2))
        svc.acquire("inst-1", "c1", "c1", self._now())
        svc.acquire("inst-1", "c1", "c2", self._now())
        with pytest.raises(ValueError, match="exhausted"):
            svc.acquire("inst-1", "c1", "c3", self._now())

    def test_evicts_idle_on_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool()
        svc.configure("inst-1", PoolConfig(consumer_id="c1", max_connections=2))
        svc.acquire("inst-1", "c1", "c1", self._now())
        svc.acquire("inst-1", "c1", "c2", self._now())
        svc.release("inst-1", "c1", "c1", self._now())  # c1 now idle
        conn = svc.acquire("inst-1", "c1", "c3", self._now())  # evicts idle c1
        assert conn.state == "active"

    def test_cleanup_idle(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool()
        svc.configure("inst-1", PoolConfig(consumer_id="c1", idle_timeout_seconds=60))
        svc.acquire("inst-1", "c1", "c1", self._now())
        svc.release("inst-1", "c1", "c1", self._now())
        closed = svc.cleanup("inst-1", "c1", self._now() + timedelta(seconds=120))
        assert closed == 1

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool()
        svc.configure("inst-1", PoolConfig(consumer_id="c1", max_connections=10))
        svc.acquire("inst-1", "c1", "c1", self._now())
        svc.acquire("inst-1", "c1", "c2", self._now())
        svc.release("inst-1", "c1", "c1", self._now())
        stats = svc.get_stats("inst-1", "c1")
        assert stats.active == 1 and stats.idle == 1 and stats.utilization_pct == 20.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiConnectionPool()
        svc.acquire("inst-1", "c1", "c1", self._now())
        stats = svc.get_stats("inst-2", "c1")
        assert stats.total == 0
