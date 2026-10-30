from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_canary import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanary, CanaryConfig,
)

class TestRequestCanary:
    def test_routing(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanary()
        svc.create("inst-1", CanaryConfig(canary_id="c1", endpoint="/api", method="GET", canary_pct=50))
        results = {svc.route("inst-1", "c1", f"consumer-{i}") for i in range(100)}
        assert "canary" in results and "stable" in results

    def test_deterministic(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanary()
        svc.create("inst-1", CanaryConfig(canary_id="c1", endpoint="/api", method="GET", canary_pct=50))
        r1 = svc.route("inst-1", "c1", "fixed-consumer")
        r2 = svc.route("inst-1", "c1", "fixed-consumer")
        assert r1 == r2

    def test_rollback_detection(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanary()
        svc.create("inst-1", CanaryConfig(canary_id="c1", endpoint="/api", method="GET"))
        config = svc._canaries[("inst-1", "c1")]
        config.canary_requests = 20
        config.canary_errors = 5
        assert config.should_rollback is True

    def test_promote(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanary()
        svc.create("inst-1", CanaryConfig(canary_id="c1", endpoint="/api", method="GET", canary_pct=10))
        svc.promote("inst-1", "c1")
        assert svc._canaries[("inst-1", "c1")].canary_pct == 100

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCanary()
        svc.create("inst-1", CanaryConfig(canary_id="c1", endpoint="/api", method="GET"))
        assert len(svc.list_canaries("inst-2")) == 0
