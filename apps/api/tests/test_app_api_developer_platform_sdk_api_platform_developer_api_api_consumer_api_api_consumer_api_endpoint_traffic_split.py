import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_traffic_split import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplit, SplitConfig, TrafficTarget,
)

class TestEndpointTrafficSplit:
    def test_route_deterministic(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplit()
        cfg = SplitConfig(endpoint_path="/api/v1/users", targets=[
            TrafficTarget(target_id="v1", version="1.0", weight=50),
            TrafficTarget(target_id="v2", version="2.0", weight=50),
        ])
        svc.set_split("inst-1", cfg)
        r1 = svc.route("inst-1", "/api/v1/users", "consumer-abc")
        r2 = svc.route("inst-1", "/api/v1/users", "consumer-abc")
        assert r1.target_id == r2.target_id  # sticky

    def test_invalid_weights(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplit()
        with pytest.raises(ValueError, match="sum to 100"):
            svc.set_split("inst-1", SplitConfig(endpoint_path="/x", targets=[
                TrafficTarget(target_id="a", version="1", weight=30),
                TrafficTarget(target_id="b", version="2", weight=30),
            ]))

    def test_full_canary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplit()
        cfg = SplitConfig(endpoint_path="/api", targets=[
            TrafficTarget(target_id="stable", version="1.0", weight=90),
            TrafficTarget(target_id="canary", version="2.0", weight=10),
        ])
        svc.set_split("inst-1", cfg)
        results = {svc.route("inst-1", "/api", f"c{i}").target_id for i in range(100)}
        assert "stable" in results  # at 90%, very likely

    def test_100_pct_single(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplit()
        cfg = SplitConfig(endpoint_path="/api", targets=[TrafficTarget(target_id="only", version="1.0", weight=100)])
        svc.set_split("inst-1", cfg)
        r = svc.route("inst-1", "/api", "any")
        assert r.target_id == "only"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointTrafficSplit()
        svc.set_split("inst-1", SplitConfig(endpoint_path="/x", targets=[TrafficTarget(target_id="a", version="1", weight=100)]))
        assert len(svc.list_splits("inst-2")) == 0
