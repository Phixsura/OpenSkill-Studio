"""Tests for App Tenant Usage Summary — metrics, health, growth."""

import pytest

from app.services.app_tenant_usage_summary import AppTenantUsageSummary

METRICS = [
    {"metric": "api_calls", "current": 8000, "limit": 10000, "previous_period": 6000},
    {"metric": "storage_mb", "current": 400, "limit": 500, "previous_period": 350},
    {"metric": "webhooks", "current": 15, "limit": 100, "previous_period": 10},
]


class TestComputeSummary:
    def test_compute(self):
        s = AppTenantUsageSummary()
        summary = s.compute_summary("inst-1", METRICS, total_cost_cents=2500)
        assert len(summary.metrics) == 3
        assert summary.total_cost_cents == 2500

    def test_health_warning(self):
        s = AppTenantUsageSummary()
        summary = s.compute_summary("inst-1", METRICS)
        assert summary.health == "warning"  # storage at 80%

    def test_health_critical(self):
        s = AppTenantUsageSummary()
        summary = s.compute_summary("inst-1", [
            {"metric": "api_calls", "current": 9800, "limit": 10000},
        ])
        assert summary.health == "critical"

    def test_health_healthy(self):
        s = AppTenantUsageSummary()
        summary = s.compute_summary("inst-1", [
            {"metric": "api_calls", "current": 1000, "limit": 10000},
        ])
        assert summary.health == "healthy"


class TestMetricProperties:
    def test_usage_pct(self):
        s = AppTenantUsageSummary()
        summary = s.compute_summary("inst-1", METRICS)
        api = next(m for m in summary.metrics if m.metric == "api_calls")
        assert api.usage_pct == 80.0

    def test_growth_pct(self):
        s = AppTenantUsageSummary()
        summary = s.compute_summary("inst-1", METRICS)
        api = next(m for m in summary.metrics if m.metric == "api_calls")
        assert api.growth_pct == pytest.approx(33.3, abs=0.1)

    def test_zero_previous(self):
        s = AppTenantUsageSummary()
        summary = s.compute_summary("inst-1", [
            {"metric": "x", "current": 100, "limit": 1000, "previous_period": 0},
        ])
        assert summary.metrics[0].growth_pct == 0


class TestGetSummary:
    def test_get(self):
        s = AppTenantUsageSummary()
        s.compute_summary("inst-1", METRICS)
        assert s.get_summary("inst-1").installation_id == "inst-1"

    def test_not_found(self):
        s = AppTenantUsageSummary()
        with pytest.raises(KeyError):
            s.get_summary("inst-1")
