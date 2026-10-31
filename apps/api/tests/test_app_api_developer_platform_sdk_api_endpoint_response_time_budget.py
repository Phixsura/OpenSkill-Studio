from app.services.app_api_developer_platform_sdk_api_endpoint_response_time_budget import AppAPIDeveloperPlatformSDKApiEndpointResponseTimeBudget

class TestResponseTimeBudget:
    def test_within_budget(self):
        b = AppAPIDeveloperPlatformSDKApiEndpointResponseTimeBudget()
        b.set_budget("inst-1", "/api/users", 200)
        r = b.check("inst-1", "/api/users", 30, 80, 150)
        assert r.within_budget is True
        assert r.headroom_pct == 25.0

    def test_over_budget(self):
        b = AppAPIDeveloperPlatformSDKApiEndpointResponseTimeBudget()
        b.set_budget("inst-1", "/api", 100)
        r = b.check("inst-1", "/api", 50, 90, 150)
        assert r.within_budget is False
        assert r.violations == 1

    def test_violation_rate(self):
        b = AppAPIDeveloperPlatformSDKApiEndpointResponseTimeBudget()
        b.set_budget("inst-1", "/api", 100)
        b.check("inst-1", "/api", 30, 60, 80)
        b.check("inst-1", "/api", 50, 90, 150)
        r = b.all_budgets("inst-1")[0]
        assert r.violation_rate == 50.0

    def test_over_budget_list(self):
        b = AppAPIDeveloperPlatformSDKApiEndpointResponseTimeBudget()
        b.set_budget("inst-1", "/fast", 200)
        b.set_budget("inst-1", "/slow", 50)
        b.check("inst-1", "/fast", 20, 50, 100)
        b.check("inst-1", "/slow", 30, 60, 100)
        assert len(b.over_budget("inst-1")) == 1

    def test_isolation(self):
        b = AppAPIDeveloperPlatformSDKApiEndpointResponseTimeBudget()
        b.set_budget("inst-1", "/api", 200)
        assert len(b.all_budgets("inst-2")) == 0
