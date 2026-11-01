from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_gateway_health import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiGatewayHealth, GatewayNode,
)

class TestGatewayHealth:
    def test_healthy_and_unhealthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiGatewayHealth()
        svc.update_node("inst-1", GatewayNode(node_id="n1", region="us-east", healthy=True, requests_per_second=100))
        svc.update_node("inst-1", GatewayNode(node_id="n2", region="eu-west", healthy=False, requests_per_second=0))
        assert len(svc.healthy_nodes("inst-1")) == 1
        assert len(svc.unhealthy_nodes("inst-1")) == 1

    def test_by_region(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiGatewayHealth()
        svc.update_node("inst-1", GatewayNode(node_id="n1", region="us-east"))
        svc.update_node("inst-1", GatewayNode(node_id="n2", region="us-east"))
        svc.update_node("inst-1", GatewayNode(node_id="n3", region="eu-west"))
        regions = svc.by_region("inst-1")
        assert len(regions["us-east"]) == 2

    def test_total_rps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiGatewayHealth()
        svc.update_node("inst-1", GatewayNode(node_id="n1", region="us", requests_per_second=50.5))
        svc.update_node("inst-1", GatewayNode(node_id="n2", region="eu", requests_per_second=30.5))
        assert svc.total_rps("inst-1") == 81.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiGatewayHealth()
        svc.update_node("inst-1", GatewayNode(node_id="n1", region="us"))
        assert len(svc.list_nodes("inst-2")) == 0
