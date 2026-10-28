"""Tests for App API Request Quota Pool — create, allocate, consume."""

import pytest
from app.services.app_api_request_quota_pool import AppAPIRequestQuotaPool


class TestCreate:
    def test_create(self):
        p = AppAPIRequestQuotaPool()
        pool = p.create_pool("inst-1", "p1", "Shared Pool", 1000)
        assert pool.available == 1000


class TestAllocate:
    def test_allocate(self):
        p = AppAPIRequestQuotaPool()
        p.create_pool("inst-1", "p1", "Pool", 100)
        allocated = p.allocate("inst-1", "p1", "consumer-a", 30)
        assert allocated == 30
        assert p.get_pool("inst-1", "p1").available == 70

    def test_over_allocate(self):
        p = AppAPIRequestQuotaPool()
        p.create_pool("inst-1", "p1", "Pool", 10)
        p.allocate("inst-1", "p1", "a", 10)
        with pytest.raises(ValueError, match="No capacity"):
            p.allocate("inst-1", "p1", "b", 5)


class TestConsume:
    def test_utilization(self):
        p = AppAPIRequestQuotaPool()
        p.create_pool("inst-1", "p1", "Pool", 100)
        p.consume("inst-1", "p1", 50)
        assert p.get_pool("inst-1", "p1").utilization_pct == 50.0


class TestIsolation:
    def test_cross(self):
        p = AppAPIRequestQuotaPool()
        p.create_pool("inst-1", "p1", "Pool", 100)
        assert p.list_pools("inst-2") == []
