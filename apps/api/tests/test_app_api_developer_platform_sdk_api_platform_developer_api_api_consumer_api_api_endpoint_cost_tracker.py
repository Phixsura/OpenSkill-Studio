from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_cost_tracker import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCostTracker

class TestEndpointCostTracker:
    def test_track_cost(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCostTracker()
        svc.set_cost("inst-1", "/users", "GET", 0.01)
        ec = svc.record_request("inst-1", "/users", "GET", 1000)
        assert ec.total_cost_cents == 10.0
        assert ec.total_dollars == "$0.10"

    def test_total_cost(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCostTracker()
        svc.set_cost("inst-1", "/a", "GET", 0.01)
        svc.set_cost("inst-1", "/b", "POST", 0.05)
        svc.record_request("inst-1", "/a", "GET", 1000)
        svc.record_request("inst-1", "/b", "POST", 200)
        assert svc.total_cost("inst-1") == 20.0  # 10 + 10

    def test_most_expensive(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCostTracker()
        svc.set_cost("inst-1", "/cheap", "GET", 0.001)
        svc.set_cost("inst-1", "/expensive", "POST", 1.0)
        svc.record_request("inst-1", "/cheap", "GET", 100)
        svc.record_request("inst-1", "/expensive", "POST", 100)
        top = svc.most_expensive("inst-1", 1)
        assert top[0].endpoint == "/expensive"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCostTracker()
        svc.set_cost("inst-1", "/api", "GET", 0.01)
        assert len(svc.list_costs("inst-2")) == 0
