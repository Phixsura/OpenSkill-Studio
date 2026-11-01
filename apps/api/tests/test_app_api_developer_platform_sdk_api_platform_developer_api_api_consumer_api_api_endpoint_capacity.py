from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_capacity import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCapacity

class TestEndpointCapacity:
    def test_set_and_utilization(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCapacity()
        svc.set_capacity("inst-1", "/api", "GET", max_rps=100)
        cap = svc.update_load("inst-1", "/api", "GET", current_rps=50)
        assert cap.utilization_pct == 50.0 and cap.status == "moderate"

    def test_saturated(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCapacity()
        svc.set_capacity("inst-1", "/api", "POST", max_rps=100)
        svc.update_load("inst-1", "/api", "POST", current_rps=95)
        assert len(svc.saturated_endpoints("inst-1", 80)) == 1

    def test_status_levels(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCapacity()
        svc.set_capacity("inst-1", "/api", "GET", max_rps=100)
        svc.update_load("inst-1", "/api", "GET", current_rps=98)
        cap = svc._capacities[("inst-1", "GET", "/api")]
        assert cap.status == "saturated"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCapacity()
        svc.set_capacity("inst-1", "/api", "GET", max_rps=100)
        assert len(svc.list_capacities("inst-2")) == 0
