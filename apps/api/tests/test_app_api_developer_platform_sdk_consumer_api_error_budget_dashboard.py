import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_error_budget_dashboard import (
    AppAPIDeveloperPlatformSDKConsumerApiErrorBudgetDashboard, ErrorBudgetEntry,
)

class TestErrorBudgetDashboard:
    def test_healthy_budget(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiErrorBudgetDashboard()
        svc.set_entry("inst-1", "c1", ErrorBudgetEntry(endpoint_path="/api/users", slo_target_pct=99.9, current_availability_pct=99.95, budget_total=100, budget_consumed_pct=50, budget_remaining_pct=50, burn_rate=1.0))
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert dashboard.overall_budget_pct == 50 and dashboard.endpoints_at_risk == 0

    def test_at_risk(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiErrorBudgetDashboard()
        svc.set_entry("inst-1", "c1", ErrorBudgetEntry(endpoint_path="/api", slo_target_pct=99.9, current_availability_pct=99.85, budget_total=100, budget_consumed_pct=90, budget_remaining_pct=10, burn_rate=5.0))
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert dashboard.endpoints_at_risk == 1

    def test_exhausted(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiErrorBudgetDashboard()
        svc.set_entry("inst-1", "c1", ErrorBudgetEntry(endpoint_path="/api", slo_target_pct=99.9, current_availability_pct=99.0, budget_total=100, budget_consumed_pct=100, budget_remaining_pct=0, burn_rate=10.0))
        assert svc.get_dashboard("inst-1", "c1").endpoints_exhausted == 1

    def test_sorted_by_remaining(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiErrorBudgetDashboard()
        svc.set_entry("inst-1", "c1", ErrorBudgetEntry(endpoint_path="/good", slo_target_pct=99.9, current_availability_pct=99.99, budget_total=100, budget_consumed_pct=10, budget_remaining_pct=90, burn_rate=0.5))
        svc.set_entry("inst-1", "c1", ErrorBudgetEntry(endpoint_path="/bad", slo_target_pct=99.9, current_availability_pct=99.0, budget_total=100, budget_consumed_pct=100, budget_remaining_pct=0, burn_rate=10))
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert dashboard.entries[0].endpoint_path == "/bad"

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiErrorBudgetDashboard()
        assert svc.get_dashboard("inst-1", "c1").overall_budget_pct == 100

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiErrorBudgetDashboard()
        svc.set_entry("inst-1", "c1", ErrorBudgetEntry(endpoint_path="/api", slo_target_pct=99.9, current_availability_pct=99.9, budget_total=100, budget_consumed_pct=50, budget_remaining_pct=50, burn_rate=1))
        assert len(svc.get_dashboard("inst-2", "c1").entries) == 0
