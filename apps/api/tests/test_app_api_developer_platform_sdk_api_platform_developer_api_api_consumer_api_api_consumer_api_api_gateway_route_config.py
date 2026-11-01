import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_api_gateway_route_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfig, RouteRule,
)

class TestApiGatewayRouteConfig:
    def test_add_and_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfig()
        svc.add_rule("inst-1", RouteRule(rule_id="r1", path_pattern="/api/v1/users/*", methods=["GET", "POST"], target_service="user-svc"))
        result = svc.match("inst-1", "GET", "/api/v1/users/123")
        assert result.matched and result.rule.target_service == "user-svc"

    def test_no_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfig()
        svc.add_rule("inst-1", RouteRule(rule_id="r1", path_pattern="/api/v1/users/*", methods=["GET"], target_service="user-svc"))
        result = svc.match("inst-1", "DELETE", "/api/v1/users/123")
        assert not result.matched

    def test_remove_rule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfig()
        svc.add_rule("inst-1", RouteRule(rule_id="r1", path_pattern="/x", methods=["GET"], target_service="svc"))
        svc.remove_rule("inst-1", "r1")
        assert len(svc.list_rules("inst-1")) == 0

    def test_duplicate_rule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfig()
        svc.add_rule("inst-1", RouteRule(rule_id="r1", path_pattern="/x", methods=["GET"], target_service="svc"))
        with pytest.raises(ValueError, match="already exists"):
            svc.add_rule("inst-1", RouteRule(rule_id="r1", path_pattern="/y", methods=["GET"], target_service="svc2"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiGatewayRouteConfig()
        svc.add_rule("inst-1", RouteRule(rule_id="r1", path_pattern="/api/*", methods=["GET"], target_service="svc"))
        assert not svc.match("inst-2", "GET", "/api/test").matched
