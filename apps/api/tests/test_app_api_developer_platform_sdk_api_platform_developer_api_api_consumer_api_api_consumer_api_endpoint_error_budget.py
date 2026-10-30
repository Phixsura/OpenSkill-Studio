import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_endpoint_error_budget import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointErrorBudget,
)

class TestConsumerEndpointErrorBudget:
    def test_track_budget(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointErrorBudget()
        svc.create("inst-1", "c1", "/api", "GET", slo_pct=99.0)
        for _ in range(95): svc.record("inst-1", "c1", "/api", "GET", False)
        for _ in range(5): svc.record("inst-1", "c1", "/api", "GET", True)
        b = svc._budgets[("inst-1", "c1", "GET", "/api")]
        assert b.budget_used_pct == 50.0 and b.status == "warning"

    def test_exhausted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointErrorBudget()
        svc.create("inst-1", "c1", "/api", "GET", slo_pct=99.0)
        for _ in range(85): svc.record("inst-1", "c1", "/api", "GET", False)
        for _ in range(15): svc.record("inst-1", "c1", "/api", "GET", True)
        assert svc._budgets[("inst-1", "c1", "GET", "/api")].status == "exhausted"

    def test_at_risk(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointErrorBudget()
        svc.create("inst-1", "c1", "/api", "POST", slo_pct=99.0)
        for _ in range(91): svc.record("inst-1", "c1", "/api", "POST", False)
        for _ in range(9): svc.record("inst-1", "c1", "/api", "POST", True)
        assert len(svc.at_risk("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointErrorBudget()
        svc.create("inst-1", "c1", "/api", "GET")
        assert len(svc.list_budgets("inst-2")) == 0
