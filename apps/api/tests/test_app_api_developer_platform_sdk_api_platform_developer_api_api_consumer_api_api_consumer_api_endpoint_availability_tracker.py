from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_availability_tracker import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTracker

class TestEndpointAvailabilityTracker:
    def test_availability(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTracker()
        for _ in range(99): svc.record_check("inst-1", "/api", "GET", True)
        svc.record_check("inst-1", "/api", "GET", False)
        w = svc._windows[("inst-1", "GET", "/api")]
        assert w.availability_pct == 99.0

    def test_down_detection(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTracker()
        svc.record_check("inst-1", "/api", "GET", False)
        assert len(svc.down_endpoints("inst-1")) == 1

    def test_below_sla(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTracker()
        for _ in range(990): svc.record_check("inst-1", "/api", "GET", True)
        for _ in range(10): svc.record_check("inst-1", "/api", "GET", False)
        assert len(svc.below_sla("inst-1", 99.9)) == 1

    def test_streak(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTracker()
        svc.record_check("inst-1", "/api", "GET", True)
        svc.record_check("inst-1", "/api", "GET", True)
        svc.record_check("inst-1", "/api", "GET", True)
        w = svc._windows[("inst-1", "GET", "/api")]
        assert w.current_streak == 3

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointAvailabilityTracker()
        svc.record_check("inst-1", "/api", "GET", True)
        assert len(svc.list_windows("inst-2")) == 0
