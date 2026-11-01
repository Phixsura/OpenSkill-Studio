"""Tests for Consumer API Connection Pool service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_conn_pool import ConnectionPoolManager


class TestConnectionPoolManager:
    def test_create_pool(self):
        svc = ConnectionPoolManager()
        result = svc.create_pool("p1", "DB Pool", max_size=10, min_size=3)
        assert result["initial_connections"] == 3

    def test_acquire(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "Pool", max_size=5, min_size=2)
        result = svc.acquire("p1")
        assert result["acquired"] is True

    def test_acquire_creates_new(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "Pool", max_size=5, min_size=1)
        svc.acquire("p1")  # uses existing
        result = svc.acquire("p1")  # creates new
        assert result["acquired"] is True
        assert result.get("new_connection") is True

    def test_pool_exhausted(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "Pool", max_size=2, min_size=2)
        svc.acquire("p1")
        svc.acquire("p1")
        result = svc.acquire("p1")
        assert result["acquired"] is False
        assert result["reason"] == "pool_exhausted"

    def test_release(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "Pool", max_size=2, min_size=1)
        acq = svc.acquire("p1")
        svc.release("p1", acq["conn_id"])
        status = svc.get_pool_status("p1")
        assert status["idle"] == 1

    def test_close_connection(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "Pool", max_size=5, min_size=2)
        acq = svc.acquire("p1")
        svc.close_connection("p1", acq["conn_id"])
        status = svc.get_pool_status("p1")
        assert status["total"] == 1

    def test_pool_status(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "DB", max_size=10, min_size=3)
        svc.acquire("p1")
        status = svc.get_pool_status("p1")
        assert status["active"] == 1
        assert status["idle"] == 2
        assert status["total"] == 3

    def test_list_pools(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "A")
        svc.create_pool("p2", "B")
        assert len(svc.list_pools()) == 2

    def test_stats(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "Pool", min_size=3)
        svc.acquire("p1")
        stats = svc.get_stats()
        assert stats["total_connections"] == 3
        assert stats["total_active"] == 1

    def test_invalid_sizes(self):
        svc = ConnectionPoolManager()
        with pytest.raises(ValueError):
            svc.create_pool("p1", "X", max_size=2, min_size=5)

    def test_duplicate(self):
        svc = ConnectionPoolManager()
        svc.create_pool("p1", "X")
        with pytest.raises(ValueError):
            svc.create_pool("p1", "Y")

    def test_isolation(self):
        a, b = ConnectionPoolManager(), ConnectionPoolManager()
        a.create_pool("p1", "X")
        assert b.get_pool_status("p1")["error"] == "not_found"
