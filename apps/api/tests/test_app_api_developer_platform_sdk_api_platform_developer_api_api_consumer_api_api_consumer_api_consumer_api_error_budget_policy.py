import pytest
from pytest import approx
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_error_budget_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy, ErrorBudgetPolicy,
)

class TestConsumerApiErrorBudgetPolicy:
    def test_healthy_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy()
        svc.set_policy("inst-1", ErrorBudgetPolicy(policy_id="p1", consumer_id="c1", slo_target_pct=99.9))
        state = svc.record("inst-1", "c1", total_requests=10000, error_count=5)
        assert state.budget_remaining_pct > 0 and not state.alert

    def test_budget_exhausted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy()
        svc.set_policy("inst-1", ErrorBudgetPolicy(policy_id="p1", consumer_id="c1", slo_target_pct=99.9))
        state = svc.record("inst-1", "c1", total_requests=1000, error_count=10)
        # Budget = 0.1% of 1000 = 1.0, consumed 10 = 1000%
        assert state.budget_remaining_pct == 0 and state.alert

    def test_burn_rate_alert(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy()
        svc.set_policy("inst-1", ErrorBudgetPolicy(policy_id="p1", consumer_id="c1", slo_target_pct=99.9, burn_rate_threshold=5.0))
        state = svc.record("inst-1", "c1", total_requests=10000, error_count=10, hours_elapsed=1.0)
        assert state.burn_rate == 10.0 and state.alert

    def test_invalid_slo(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy()
        with pytest.raises(ValueError, match="slo_target_pct"):
            svc.set_policy("inst-1", ErrorBudgetPolicy(policy_id="p1", consumer_id="c1", slo_target_pct=50))

    def test_get_state(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy()
        svc.set_policy("inst-1", ErrorBudgetPolicy(policy_id="p1", consumer_id="c1", slo_target_pct=99.0))
        svc.record("inst-1", "c1", total_requests=1000, error_count=5)
        state = svc.get_state("inst-1", "c1")
        assert state is not None and state.budget_total == approx(10.0)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorBudgetPolicy()
        svc.set_policy("inst-1", ErrorBudgetPolicy(policy_id="p1", consumer_id="c1", slo_target_pct=99.9))
        assert svc.get_policy("inst-2", "c1") is None
