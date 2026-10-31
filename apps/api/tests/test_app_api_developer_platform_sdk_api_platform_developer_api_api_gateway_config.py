import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_gateway_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfig, RouteConfig,
)

class TestApiGatewayConfig:
    def test_add_and_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfig()
        svc.add_route("inst-1", RouteConfig(route_id="r1", path_pattern="/api/v1/users/*", upstream="http://users:8080", middlewares=["auth", "logging"]))
        m = svc.match_route("inst-1", "GET", "/api/v1/users/123")
        assert m is not None and m.upstream == "http://users:8080"

    def test_no_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfig()
        svc.add_route("inst-1", RouteConfig(route_id="r1", path_pattern="/api/v1/orders", upstream="http://orders:8080"))
        assert svc.match_route("inst-1", "GET", "/api/v2/users") is None

    def test_disabled_route(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfig()
        svc.add_route("inst-1", RouteConfig(route_id="r1", path_pattern="/api/*", upstream="http://svc:8080"))
        svc.toggle_route("inst-1", "r1", False)
        assert svc.match_route("inst-1", "GET", "/api/test") is None

    def test_invalid_middleware(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfig()
        with pytest.raises(ValueError, match="Invalid middlewares"):
            svc.add_route("inst-1", RouteConfig(route_id="r1", path_pattern="/api", upstream="http://x", middlewares=["bad"]))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGatewayConfig()
        svc.add_route("inst-1", RouteConfig(route_id="r1", path_pattern="/api", upstream="http://x"))
        assert len(svc.list_routes("inst-2")) == 0
