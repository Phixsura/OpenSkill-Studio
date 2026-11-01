"""Tests for Endpoint Cost Allocator service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_cost_allocator import (
    CostAllocator, CostRecord,
)


class TestCostAllocator:
    def test_record_and_endpoint_cost(self):
        svc = CostAllocator()
        svc.record(CostRecord("ep1", "c1", "2024-01", 1000, 500, 200))
        result = svc.get_endpoint_cost("ep1")
        assert result["total_cost_cents"] == 700
        assert result["total_dollars"] == 7.0

    def test_consumer_cost(self):
        svc = CostAllocator()
        svc.record(CostRecord("ep1", "c1", "2024-01", 500, 300, 100))
        svc.record(CostRecord("ep2", "c1", "2024-01", 200, 100, 50))
        result = svc.get_consumer_cost("c1")
        assert result["total_cost_cents"] == 550
        assert len(result["by_endpoint"]) == 2

    def test_filter_by_period(self):
        svc = CostAllocator()
        svc.record(CostRecord("ep1", "c1", "2024-01", 100, 50, 10))
        svc.record(CostRecord("ep1", "c1", "2024-02", 200, 100, 20))
        result = svc.get_endpoint_cost("ep1", period="2024-01")
        assert result["total_cost_cents"] == 60

    def test_top_costs(self):
        svc = CostAllocator()
        svc.record(CostRecord("ep1", "c1", "2024-01", 100, 1000, 500))
        svc.record(CostRecord("ep1", "c2", "2024-01", 50, 200, 100))
        top = svc.get_top_costs()
        assert top[0]["consumer_id"] == "c1"
        assert top[0]["total_cents"] == 1500

    def test_period_summary(self):
        svc = CostAllocator()
        svc.record(CostRecord("ep1", "c1", "2024-01", 100, 500, 200))
        svc.record(CostRecord("ep2", "c2", "2024-01", 200, 300, 100))
        summary = svc.get_period_summary("2024-01")
        assert summary["unique_consumers"] == 2
        assert summary["unique_endpoints"] == 2
        assert summary["total_cost_cents"] == 1100

    def test_negative_requests_rejected(self):
        svc = CostAllocator()
        with pytest.raises(ValueError):
            svc.record(CostRecord("ep1", "c1", "p", -1, 0, 0))

    def test_no_data(self):
        svc = CostAllocator()
        assert svc.get_endpoint_cost("missing")["total_cost_cents"] == 0
        assert svc.get_consumer_cost("missing")["total_cost_cents"] == 0

    def test_storage_cost(self):
        svc = CostAllocator()
        svc.record(CostRecord("ep1", "c1", "p", 10, 100, 50, 25))
        result = svc.get_endpoint_cost("ep1")
        assert result["storage_cents"] == 25
        assert result["total_cost_cents"] == 175

    def test_isolation(self):
        a, b = CostAllocator(), CostAllocator()
        a.record(CostRecord("ep1", "c1", "p", 10, 100, 50))
        assert b.get_endpoint_cost("ep1")["total_cost_cents"] == 0
