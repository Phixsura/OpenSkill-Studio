"""Tests for Consumer Quota Pool service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_quota_pool import QuotaPoolManager


class TestQuotaPoolManager:
    def test_create_and_status(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "API Calls", 1000)
        status = svc.get_pool_status("p1")
        assert status["total_capacity"] == 1000
        assert status["available"] == 1000

    def test_reserve(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "Calls", 100)
        result = svc.reserve("r1", "p1", "c1", 30)
        assert result["success"] is True
        status = svc.get_pool_status("p1")
        assert status["reserved"] == 30
        assert status["available"] == 70

    def test_reserve_insufficient(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "Calls", 50)
        result = svc.reserve("r1", "p1", "c1", 60)
        assert result["success"] is False
        assert result["reason"] == "insufficient_capacity"

    def test_consume(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "Calls", 100)
        svc.reserve("r1", "p1", "c1", 20)
        result = svc.consume("r1", 15)
        assert result["consumed"] == 15
        status = svc.get_pool_status("p1")
        assert status["used"] == 15
        assert status["reserved"] == 0

    def test_consume_full_reservation(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "Calls", 100)
        svc.reserve("r1", "p1", "c1", 25)
        result = svc.consume("r1")
        assert result["consumed"] == 25

    def test_release(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "Calls", 100)
        svc.reserve("r1", "p1", "c1", 40)
        result = svc.release("r1")
        assert result["released"] is True
        assert svc.get_pool_status("p1")["available"] == 100

    def test_consumer_reservations(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "Calls", 1000)
        svc.reserve("r1", "p1", "c1", 100)
        svc.reserve("r2", "p1", "c2", 200)
        reservations = svc.get_consumer_reservations("c1")
        assert len(reservations) == 1
        assert reservations[0]["amount"] == 100

    def test_list_pools(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "A", 100)
        svc.create_pool("p2", "B", 200)
        pools = svc.list_pools()
        assert len(pools) == 2

    def test_duplicate_pool(self):
        svc = QuotaPoolManager()
        svc.create_pool("p1", "X", 100)
        with pytest.raises(ValueError):
            svc.create_pool("p1", "Y", 200)

    def test_zero_capacity(self):
        svc = QuotaPoolManager()
        with pytest.raises(ValueError):
            svc.create_pool("p1", "X", 0)

    def test_isolation(self):
        a, b = QuotaPoolManager(), QuotaPoolManager()
        a.create_pool("p1", "X", 100)
        assert b.get_pool_status("p1") == {"error": "not_found"}
