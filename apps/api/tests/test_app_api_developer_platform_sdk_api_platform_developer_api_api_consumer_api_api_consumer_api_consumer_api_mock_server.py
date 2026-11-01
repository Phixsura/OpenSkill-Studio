import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_mock_server import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer, MockRoute,
)

class TestConsumerApiMockServer:
    def test_add_and_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer()
        svc.add_route("inst-1", "c1", MockRoute(route_id="r1", method="GET", path_pattern="/api/users/*", response_status=200, response_body='[{"id":"1"}]'))
        resp = svc.match("inst-1", "c1", "GET", "/api/users/123")
        assert resp.matched and resp.status == 200

    def test_no_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer()
        svc.add_route("inst-1", "c1", MockRoute(route_id="r1", method="GET", path_pattern="/api/users"))
        resp = svc.match("inst-1", "c1", "POST", "/api/users")
        assert not resp.matched

    def test_call_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer()
        svc.add_route("inst-1", "c1", MockRoute(route_id="r1", method="GET", path_pattern="/api"))
        svc.match("inst-1", "c1", "GET", "/api")
        svc.match("inst-1", "c1", "GET", "/api")
        assert svc.get_call_count("inst-1", "c1", "r1") == 2

    def test_disabled_route(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer()
        svc.add_route("inst-1", "c1", MockRoute(route_id="r1", method="GET", path_pattern="/api", enabled=False))
        resp = svc.match("inst-1", "c1", "GET", "/api")
        assert not resp.matched

    def test_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer()
        svc.add_route("inst-1", "c1", MockRoute(route_id="r1", method="GET", path_pattern="/api"))
        svc.remove_route("inst-1", "c1", "r1")
        assert len(svc.list_routes("inst-1", "c1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiMockServer()
        svc.add_route("inst-1", "c1", MockRoute(route_id="r1", method="GET", path_pattern="/api"))
        assert not svc.match("inst-2", "c1", "GET", "/api").matched
