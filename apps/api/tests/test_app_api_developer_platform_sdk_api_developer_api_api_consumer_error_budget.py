from app.services.app_api_developer_platform_sdk_api_developer_api_api_consumer_error_budget import AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudget

class TestConsumerErrorBudget:
    def test_create(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudget()
        eb = b.create("inst-1", "c1", 99.9)
        assert eb.budget_remaining_pct == 0.1  # 100 - 99.9

    def test_recording(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudget()
        b.create("inst-1", "c1", 99.0)
        for _ in range(99): b.record("inst-1", "c1", True)
        b.record("inst-1", "c1", False)
        eb = b.all_budgets("inst-1")[0]
        assert eb.current_success_pct == 99.0

    def test_exhausted(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudget()
        b.create("inst-1", "c1", 99.0)
        for _ in range(95): b.record("inst-1", "c1", True)
        for _ in range(5): b.record("inst-1", "c1", False)
        assert len(b.exhausted_consumers("inst-1")) == 1

    def test_burn_rate(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudget()
        b.create("inst-1", "c1", 99.0)
        for _ in range(90): b.record("inst-1", "c1", True)
        for _ in range(10): b.record("inst-1", "c1", False)
        assert b.all_budgets("inst-1")[0].burn_rate == 10.0  # 10x over budget

    def test_isolation(self):
        b = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudget()
        b.create("inst-1", "c1", 99.0)
        assert len(b.all_budgets("inst-2")) == 0
