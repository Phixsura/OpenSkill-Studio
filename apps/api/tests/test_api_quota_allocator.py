"""Tests for API Quota Allocator — pools, allocation, consumption, transfer, reclaim."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.api_quota_allocator import (
    ApiQuotaAllocator,
    QuotaType,
)


class TestPoolManagement:
    def test_create_pool(self):
        qa = ApiQuotaAllocator()
        pool = qa.create_pool("org-1", QuotaType.REQUESTS, 10_000)
        assert pool.total == 10_000
        assert pool.reserved == 0
        assert pool.available == 10_000

    def test_get_pool(self):
        qa = ApiQuotaAllocator()
        qa.create_pool("org-1", QuotaType.REQUESTS, 5000)
        pool = qa.get_pool("org-1", QuotaType.REQUESTS)
        assert pool is not None
        assert pool.total == 5000

    def test_get_nonexistent_pool(self):
        qa = ApiQuotaAllocator()
        assert qa.get_pool("org-x", QuotaType.REQUESTS) is None

    def test_resize_pool_up(self):
        qa = ApiQuotaAllocator()
        qa.create_pool("org-1", QuotaType.STORAGE_MB, 1000)
        pool = qa.resize_pool("org-1", QuotaType.STORAGE_MB, 2000)
        assert pool.total == 2000

    def test_resize_pool_down_blocked(self):
        qa = ApiQuotaAllocator()
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 800)
        with pytest.raises(ValueError, match="Cannot shrink"):
            qa.resize_pool("org-1", QuotaType.REQUESTS, 500)

    def test_resize_nonexistent_raises(self):
        qa = ApiQuotaAllocator()
        with pytest.raises(ValueError, match="not found"):
            qa.resize_pool("org-x", QuotaType.REQUESTS, 100)


class TestAllocation:
    def test_allocate_success(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 300)
        assert result.success is True
        assert result.alloc_id is not None
        pool = qa.get_pool("org-1", QuotaType.REQUESTS)
        assert pool.reserved == 300

    def test_allocate_insufficient(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 100)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 200)
        assert result.success is False
        assert "Insufficient" in (result.error or "")

    def test_headroom_reserves_margin(self):
        qa = ApiQuotaAllocator(headroom_pct=10)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        # Allocatable = 900 (10% headroom)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 900)
        assert result.success is True
        # Can't allocate more even though pool.total - reserved = 100
        result2 = qa.allocate("org-1", QuotaType.REQUESTS, "app-2", "app", 50)
        assert result2.success is False

    def test_allocate_no_pool(self):
        qa = ApiQuotaAllocator()
        result = qa.allocate("org-x", QuotaType.REQUESTS, "app-1", "app", 100)
        assert result.success is False
        assert "not found" in (result.error or "")

    def test_multiple_allocations(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 400)
        qa.allocate("org-1", QuotaType.REQUESTS, "app-2", "app", 300)
        pool = qa.get_pool("org-1", QuotaType.REQUESTS)
        assert pool.reserved == 700
        assert pool.available == 300


class TestConsumption:
    def test_consume_within_limit(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 500)
        cr = qa.consume(result.alloc_id, 100)
        assert cr.allowed is True
        assert cr.remaining == 400

    def test_consume_over_limit(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 50)
        cr = qa.consume(result.alloc_id, 60)
        assert cr.allowed is False
        assert cr.over_limit is True

    def test_consume_updates_pool_used(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 500)
        qa.consume(result.alloc_id, 200)
        pool = qa.get_pool("org-1", QuotaType.REQUESTS)
        assert pool.used == 200
        assert pool.utilization_pct == pytest.approx(20.0)

    def test_consume_unknown_alloc(self):
        qa = ApiQuotaAllocator()
        cr = qa.consume("nonexistent", 10)
        assert cr.allowed is False

    def test_incremental_consumption(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.BANDWIDTH_MB, 100)
        result = qa.allocate("org-1", QuotaType.BANDWIDTH_MB, "app-1", "app", 50)
        qa.consume(result.alloc_id, 20)
        qa.consume(result.alloc_id, 20)
        alloc = qa.get_allocation(result.alloc_id)
        assert alloc.used == 40
        assert alloc.remaining == 10


class TestRelease:
    def test_release_returns_to_pool(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 300)
        assert qa.get_pool("org-1", QuotaType.REQUESTS).reserved == 300
        qa.release(result.alloc_id)
        assert qa.get_pool("org-1", QuotaType.REQUESTS).reserved == 0

    def test_release_nonexistent(self):
        qa = ApiQuotaAllocator()
        assert qa.release("nonexistent") is False

    def test_release_deducts_used(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        result = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 300)
        qa.consume(result.alloc_id, 100)
        qa.release(result.alloc_id)
        pool = qa.get_pool("org-1", QuotaType.REQUESTS)
        assert pool.used == 0
        assert pool.reserved == 0


class TestTransfer:
    def test_transfer_success(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        r1 = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 500)
        r2 = qa.allocate("org-1", QuotaType.REQUESTS, "app-2", "app", 200)
        ok = qa.transfer(r1.alloc_id, r2.alloc_id, 100)
        assert ok is True
        assert qa.get_allocation(r1.alloc_id).reserved == 400
        assert qa.get_allocation(r2.alloc_id).reserved == 300

    def test_transfer_exceeds_remaining(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        r1 = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 100)
        r2 = qa.allocate("org-1", QuotaType.REQUESTS, "app-2", "app", 100)
        qa.consume(r1.alloc_id, 80)  # only 20 remaining
        ok = qa.transfer(r1.alloc_id, r2.alloc_id, 50)
        assert ok is False

    def test_transfer_cross_pool_blocked(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        qa.create_pool("org-1", QuotaType.STORAGE_MB, 1000)
        r1 = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 100)
        r2 = qa.allocate("org-1", QuotaType.STORAGE_MB, "app-2", "app", 100)
        ok = qa.transfer(r1.alloc_id, r2.alloc_id, 50)
        assert ok is False


class TestReclaim:
    def test_reclaim_unused(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        r = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 300)
        # Backdate creation so it looks idle
        alloc = qa.get_allocation(r.alloc_id)
        alloc.created_at = datetime.now(UTC) - timedelta(hours=48)
        reclaimed = qa.reclaim_unused(idle_hours=24)
        assert r.alloc_id in reclaimed
        assert qa.get_allocation(r.alloc_id) is None

    def test_active_not_reclaimed(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        r = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 300)
        qa.consume(r.alloc_id, 200)
        reclaimed = qa.reclaim_unused(idle_hours=24)
        assert r.alloc_id not in reclaimed


class TestQueries:
    def test_get_entity_allocations(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 10000)
        qa.create_pool("org-1", QuotaType.STORAGE_MB, 5000)
        qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 1000)
        qa.allocate("org-1", QuotaType.STORAGE_MB, "app-1", "app", 500)
        allocs = qa.get_entity_allocations("app-1")
        assert len(allocs) == 2

    def test_pool_summary(self):
        qa = ApiQuotaAllocator(headroom_pct=0)
        qa.create_pool("org-1", QuotaType.REQUESTS, 1000)
        r1 = qa.allocate("org-1", QuotaType.REQUESTS, "app-1", "app", 400)
        qa.consume(r1.alloc_id, 100)
        qa.allocate("org-1", QuotaType.REQUESTS, "app-2", "app", 200)
        summary = qa.get_pool_summary("org-1", QuotaType.REQUESTS)
        assert summary is not None
        assert summary.total == 1000
        assert summary.reserved == 600
        assert summary.used == 100
        assert len(summary.allocations) == 2
        # Sorted by usage desc
        assert summary.allocations[0]["entity_id"] == "app-1"

    def test_pool_summary_nonexistent(self):
        qa = ApiQuotaAllocator()
        assert qa.get_pool_summary("org-x", QuotaType.REQUESTS) is None
