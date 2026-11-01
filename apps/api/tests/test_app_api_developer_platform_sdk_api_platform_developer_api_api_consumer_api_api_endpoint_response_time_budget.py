from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_response_time_budget import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointResponseTimeBudget

class TestEndpointResponseTimeBudget:
    def test_within_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointResponseTimeBudget()
        svc.set_budget("inst-1", "/api", "GET", 200)
        for _ in range(100): svc.record("inst-1", "/api", "GET", 150)
        b = svc._budgets[("inst-1", "GET", "/api")]
        assert b.compliance_pct == 100.0 and b.meeting_budget is True

    def test_over_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointResponseTimeBudget()
        svc.set_budget("inst-1", "/slow", "GET", 100)
        for _ in range(90): svc.record("inst-1", "/slow", "GET", 50)
        for _ in range(10): svc.record("inst-1", "/slow", "GET", 500)
        b = svc._budgets[("inst-1", "GET", "/slow")]
        assert b.compliance_pct == 90.0 and b.meeting_budget is False

    def test_violations(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointResponseTimeBudget()
        svc.set_budget("inst-1", "/api", "GET", 100)
        for _ in range(50): svc.record("inst-1", "/api", "GET", 50)
        for _ in range(50): svc.record("inst-1", "/api", "GET", 500)
        assert len(svc.violations("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointResponseTimeBudget()
        svc.set_budget("inst-1", "/api", "GET", 200)
        assert len(svc.list_budgets("inst-2")) == 0
