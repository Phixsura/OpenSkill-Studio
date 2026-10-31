from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_connection_pool import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPool

class TestConnectionPool:
    def test_acquire_and_release(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPool()
        svc.create_pool("inst-1", "c1", max_connections=5)
        assert svc.acquire("inst-1", "c1") is True
        pool = svc.get_pool("inst-1", "c1")
        assert pool.active_connections == 1
        svc.release("inst-1", "c1")
        assert pool.idle_connections == 1

    def test_reuse(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPool()
        svc.create_pool("inst-1", "c1", max_connections=5)
        svc.acquire("inst-1", "c1")
        svc.release("inst-1", "c1")  # now idle
        svc.acquire("inst-1", "c1")  # reuse
        assert svc.get_pool("inst-1", "c1").total_reused == 1

    def test_exhaustion(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPool()
        svc.create_pool("inst-1", "c1", max_connections=2)
        svc.acquire("inst-1", "c1")
        svc.acquire("inst-1", "c1")
        assert svc.acquire("inst-1", "c1") is False
        assert svc.get_pool("inst-1", "c1").total_exhausted == 1

    def test_utilization(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPool()
        svc.create_pool("inst-1", "c1", max_connections=10)
        for _ in range(5): svc.acquire("inst-1", "c1")
        assert svc.get_pool("inst-1", "c1").utilization_pct == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConnectionPool()
        svc.create_pool("inst-1", "c1")
        assert len(svc.list_pools("inst-2")) == 0
