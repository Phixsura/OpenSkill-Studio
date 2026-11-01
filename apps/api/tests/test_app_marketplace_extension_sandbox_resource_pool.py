from app.services.app_marketplace_extension_sandbox_resource_pool import (
    ResourcePoolService, ResourceKind, AllocationStatus,
)
import pytest


def test_configure_and_allocate():
    svc = ResourcePoolService()
    svc.configure_pool(ResourceKind.CPU, 8.0)
    alloc = svc.allocate("sb-1", ResourceKind.CPU, 2.0)
    assert alloc.status == AllocationStatus.ACTIVE
    status = svc.get_pool_status(ResourceKind.CPU)
    assert status["allocated"] == 2.0
    assert status["available"] == 6.0


def test_queue_when_full():
    svc = ResourcePoolService()
    svc.configure_pool(ResourceKind.MEMORY, 4.0)
    svc.allocate("sb-1", ResourceKind.MEMORY, 3.0)
    alloc2 = svc.allocate("sb-2", ResourceKind.MEMORY, 3.0)
    assert alloc2.status == AllocationStatus.QUEUED


def test_release_fulfills_queue():
    svc = ResourcePoolService()
    svc.configure_pool(ResourceKind.CPU, 4.0)
    a1 = svc.allocate("sb-1", ResourceKind.CPU, 3.0)
    a2 = svc.allocate("sb-2", ResourceKind.CPU, 2.0)  # queued
    assert a2.status == AllocationStatus.QUEUED
    svc.release(a1.allocation_id)
    assert a2.status == AllocationStatus.ACTIVE


def test_priority_queue():
    svc = ResourcePoolService()
    svc.configure_pool(ResourceKind.GPU, 1.0)
    svc.allocate("sb-1", ResourceKind.GPU, 1.0)
    low = svc.allocate("sb-2", ResourceKind.GPU, 1.0, priority=1)
    high = svc.allocate("sb-3", ResourceKind.GPU, 1.0, priority=10)
    # High priority should be first in queue
    assert svc._queue[0].allocation_id == high.allocation_id


def test_reserve():
    svc = ResourcePoolService()
    svc.configure_pool(ResourceKind.DISK_IO, 100.0)
    assert svc.reserve(ResourceKind.DISK_IO, 30.0) is True
    status = svc.get_pool_status(ResourceKind.DISK_IO)
    assert status["reserved"] == 30.0
    assert status["available"] == 70.0


def test_utilization():
    svc = ResourcePoolService()
    svc.configure_pool(ResourceKind.CPU, 10.0)
    svc.allocate("sb-1", ResourceKind.CPU, 5.0)
    status = svc.get_pool_status(ResourceKind.CPU)
    assert status["utilization_pct"] == 50.0


def test_invalid_pool():
    svc = ResourcePoolService()
    with pytest.raises(ValueError, match="No pool"):
        svc.allocate("sb-1", ResourceKind.GPU, 1.0)


def test_sandbox_allocations():
    svc = ResourcePoolService()
    svc.configure_pool(ResourceKind.CPU, 8.0)
    svc.configure_pool(ResourceKind.MEMORY, 16.0)
    svc.allocate("sb-1", ResourceKind.CPU, 2.0)
    svc.allocate("sb-1", ResourceKind.MEMORY, 4.0)
    svc.allocate("sb-2", ResourceKind.CPU, 1.0)
    allocs = svc.get_sandbox_allocations("sb-1")
    assert len(allocs) == 2
