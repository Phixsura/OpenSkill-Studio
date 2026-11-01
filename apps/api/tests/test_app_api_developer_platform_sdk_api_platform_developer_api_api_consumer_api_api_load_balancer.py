from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_load_balancer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancer, LoadBalancerConfig, BackendInstance,
)

class TestLoadBalancer:
    def test_round_robin(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancer()
        svc.configure("inst-1", LoadBalancerConfig(strategy="round_robin", instances=[BackendInstance("i1", "host1"), BackendInstance("i2", "host2")]))
        r1 = svc.select("inst-1")
        r2 = svc.select("inst-1")
        assert r1.instance_id != r2.instance_id

    def test_least_connections(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancer()
        svc.configure("inst-1", LoadBalancerConfig(strategy="least_connections", instances=[BackendInstance("i1", "h1", active_connections=10), BackendInstance("i2", "h2", active_connections=2)]))
        assert svc.select("inst-1").instance_id == "i2"

    def test_ip_hash_sticky(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancer()
        svc.configure("inst-1", LoadBalancerConfig(strategy="ip_hash", instances=[BackendInstance("i1", "h1"), BackendInstance("i2", "h2")]))
        results = {svc.select("inst-1", "consumer-1").instance_id for _ in range(10)}
        assert len(results) == 1  # consistent hashing

    def test_unhealthy_skipped(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancer()
        svc.configure("inst-1", LoadBalancerConfig(instances=[BackendInstance("i1", "h1"), BackendInstance("i2", "h2")]))
        svc.mark_unhealthy("inst-1", "i1")
        assert svc.select("inst-1").instance_id == "i2"
        assert svc.healthy_count("inst-1") == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiLoadBalancer()
        svc.configure("inst-1", LoadBalancerConfig(instances=[BackendInstance("i1", "h1")]))
        assert svc.healthy_count("inst-2") == 0
