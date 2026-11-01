from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_latency_budget import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointLatencyBudget

class TestEndpointLatencyBudget:
    def test_within_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointLatencyBudget()
        svc.set_budget("inst-1", "c1", "/api", "GET", 200)
        for _ in range(100): svc.record("inst-1", "c1", "/api", "GET", 150)
        b = svc._budgets[("inst-1", "c1", "GET", "/api")]
        assert b.compliance_pct == 100.0 and b.meeting is True

    def test_violations(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointLatencyBudget()
        svc.set_budget("inst-1", "c1", "/slow", "GET", 100)
        for _ in range(80): svc.record("inst-1", "c1", "/slow", "GET", 50)
        for _ in range(20): svc.record("inst-1", "c1", "/slow", "GET", 500)
        assert len(svc.violations("inst-1")) == 1

    def test_meeting_at_95(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointLatencyBudget()
        svc.set_budget("inst-1", "c1", "/api", "GET", 200)
        for _ in range(96): svc.record("inst-1", "c1", "/api", "GET", 100)
        for _ in range(4): svc.record("inst-1", "c1", "/api", "GET", 500)
        b = svc._budgets[("inst-1", "c1", "GET", "/api")]
        assert b.meeting is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointLatencyBudget()
        svc.set_budget("inst-1", "c1", "/api", "GET", 200)
        assert len(svc.list_budgets("inst-2")) == 0
