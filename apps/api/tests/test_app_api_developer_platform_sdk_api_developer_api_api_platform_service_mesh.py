import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_service_mesh import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMesh

class TestServiceMesh:
    def test_register(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMesh()
        r = m.register_route("inst-1", "api-gateway", "user-service", "grpc")
        assert r.protocol == "grpc"

    def test_traffic(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMesh()
        m.register_route("inst-1", "gw", "users")
        m.record_traffic("inst-1", "gw", "users", 50, True)
        m.record_traffic("inst-1", "gw", "users", 100, False)
        r = m.all_routes("inst-1")[0]
        assert r.error_rate == 50.0

    def test_routes_from(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMesh()
        m.register_route("inst-1", "gw", "users")
        m.register_route("inst-1", "gw", "orders")
        m.register_route("inst-1", "users", "db")
        assert len(m.routes_from("inst-1", "gw")) == 2

    def test_unhealthy(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMesh()
        m.register_route("inst-1", "gw", "bad")
        for _ in range(5): m.record_traffic("inst-1", "gw", "bad", 50, False)
        for _ in range(5): m.record_traffic("inst-1", "gw", "bad", 50, True)
        assert len(m.unhealthy_routes("inst-1")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMesh()
        m.register_route("inst-1", "a", "b")
        assert len(m.all_routes("inst-2")) == 0
