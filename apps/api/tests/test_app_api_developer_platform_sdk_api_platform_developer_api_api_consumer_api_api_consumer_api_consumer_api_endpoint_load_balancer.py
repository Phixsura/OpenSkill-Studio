import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_endpoint_load_balancer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer, LBConfig, BackendInstance,
)

class TestEndpointLoadBalancer:
    def test_round_robin(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer()
        svc.configure("inst-1", LBConfig(endpoint_path="/api", strategy="round_robin"))
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i1", host="h1", port=8080))
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i2", host="h2", port=8080))
        r1 = svc.route("inst-1", "/api")
        r2 = svc.route("inst-1", "/api")
        assert r1.instance_id != r2.instance_id

    def test_least_connections(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer()
        svc.configure("inst-1", LBConfig(endpoint_path="/api", strategy="least_connections"))
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i1", host="h1", port=8080, active_connections=5))
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i2", host="h2", port=8080, active_connections=1))
        r = svc.route("inst-1", "/api")
        assert r.instance_id == "i2"

    def test_unhealthy_skipped(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer()
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i1", host="h1", port=8080, healthy=False))
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i2", host="h2", port=8080, healthy=True))
        r = svc.route("inst-1", "/api")
        assert r.instance_id == "i2"

    def test_no_healthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer()
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i1", host="h1", port=8080, healthy=False))
        with pytest.raises(ValueError, match="No healthy"):
            svc.route("inst-1", "/api")

    def test_release(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer()
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i1", host="h1", port=8080))
        svc.route("inst-1", "/api")
        svc.release("inst-1", "/api", "i1")
        assert svc.list_instances("inst-1", "/api")[0].active_connections == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointLoadBalancer()
        svc.add_instance("inst-1", "/api", BackendInstance(instance_id="i1", host="h1", port=8080))
        assert len(svc.list_instances("inst-2", "/api")) == 0
