import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_request_budget_tracker import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker, BudgetConfig,
)

class TestRequestBudgetTracker:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_consume_within_budget(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker()
        svc.configure("inst-1", BudgetConfig(consumer_id="c1", daily_budget=100, monthly_budget=3000))
        state = svc.consume("inst-1", "c1", self._now(), 10)
        assert state.daily_used == 10 and state.daily_pct == 10.0 and not state.blocked

    def test_alert_threshold(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker()
        svc.configure("inst-1", BudgetConfig(consumer_id="c1", daily_budget=100, monthly_budget=3000, alert_threshold_pct=80))
        svc.consume("inst-1", "c1", self._now(), 85)
        state = svc.get_state("inst-1", "c1", self._now())
        assert state.alert_triggered and state.daily_pct == 85.0

    def test_auto_block(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker()
        svc.configure("inst-1", BudgetConfig(consumer_id="c1", daily_budget=10, monthly_budget=300, auto_block=True))
        svc.consume("inst-1", "c1", self._now(), 15)
        state = svc.get_state("inst-1", "c1", self._now())
        assert state.blocked

    def test_monthly_tracking(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker()
        svc.configure("inst-1", BudgetConfig(consumer_id="c1", daily_budget=1000, monthly_budget=100))
        svc.consume("inst-1", "c1", self._now(), 80)
        state = svc.get_state("inst-1", "c1", self._now())
        assert state.monthly_pct == 80.0

    def test_invalid_config(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker()
        with pytest.raises(ValueError, match="monthly_budget"):
            svc.configure("inst-1", BudgetConfig(consumer_id="c1", daily_budget=1000, monthly_budget=500))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiRequestBudgetTracker()
        svc.consume("inst-1", "c1", self._now(), 50)
        state = svc.get_state("inst-2", "c1", self._now())
        assert state.daily_used == 0
