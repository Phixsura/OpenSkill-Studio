import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_gateway_middleware import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware, Middleware,
)

class TestConsumerApiGatewayMiddleware:
    def test_add_and_execute(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware()
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m1", name="Auth", middleware_type="auth", order=1))
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m2", name="Rate Limit", middleware_type="rate_limit", order=2))
        result = svc.execute_chain("inst-1", "c1")
        assert result.executed == 2 and result.chain == ["Auth", "Rate Limit"]

    def test_order(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware()
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m2", name="B", middleware_type="logging", order=2))
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m1", name="A", middleware_type="auth", order=1))
        chain = svc.get_chain("inst-1", "c1")
        assert chain[0].name == "A"

    def test_disabled_skipped(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware()
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m1", name="Auth", middleware_type="auth", enabled=False))
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m2", name="Log", middleware_type="logging"))
        result = svc.execute_chain("inst-1", "c1")
        assert result.executed == 1 and result.skipped == 1

    def test_duplicate_id(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware()
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m1", name="A", middleware_type="auth"))
        with pytest.raises(ValueError, match="already exists"):
            svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m1", name="B", middleware_type="logging"))

    def test_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware()
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m1", name="Auth", middleware_type="auth"))
        svc.remove_middleware("inst-1", "c1", "m1")
        assert len(svc.get_chain("inst-1", "c1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddleware()
        svc.add_middleware("inst-1", "c1", Middleware(middleware_id="m1", name="A", middleware_type="auth"))
        assert len(svc.get_chain("inst-2", "c1")) == 0
