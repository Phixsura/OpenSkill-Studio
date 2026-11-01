"""Tests for App Connection Pool — registration, status, saturation."""

import pytest

from app.services.app_connection_pool import AppConnectionPool


class TestRegister:
    def test_register(self):
        p = AppConnectionPool()
        s = p.register_pool("inst-1", "main-db", 20)
        assert s.max_size == 20
        assert s.idle == 20

    def test_invalid_size(self):
        p = AppConnectionPool()
        with pytest.raises(ValueError):
            p.register_pool("inst-1", "db", 0)


class TestUpdate:
    def test_update(self):
        p = AppConnectionPool()
        p.register_pool("inst-1", "db", 20)
        s = p.update_status("inst-1", "db", active=15, idle=5, waiting=3, avg_acquire_ms=12.5)
        assert s.active == 15
        assert s.waiting == 3
        assert s.avg_acquire_ms == 12.5


class TestAcquisition:
    def test_record(self):
        p = AppConnectionPool()
        p.register_pool("inst-1", "db", 20)
        p.record_acquisition("inst-1", "db")
        p.record_acquisition("inst-1", "db", timed_out=True)
        s = p.get_pool("inst-1", "db")
        assert s.total_acquired == 2
        assert s.total_timeouts == 1


class TestSaturation:
    def test_saturated(self):
        p = AppConnectionPool()
        p.register_pool("inst-1", "db", 10)
        p.update_status("inst-1", "db", active=10, idle=0, waiting=5)
        assert p.is_saturated("inst-1", "db") is True

    def test_not_saturated(self):
        p = AppConnectionPool()
        p.register_pool("inst-1", "db", 10)
        p.update_status("inst-1", "db", active=5, idle=5, waiting=0)
        assert p.is_saturated("inst-1", "db") is False


class TestUtilization:
    def test_pct(self):
        p = AppConnectionPool()
        p.register_pool("inst-1", "db", 20)
        p.update_status("inst-1", "db", active=10, idle=10, waiting=0)
        assert p.utilization_pct("inst-1", "db") == 50.0


class TestIsolation:
    def test_cross_installation(self):
        p = AppConnectionPool()
        p.register_pool("inst-1", "db", 10)
        with pytest.raises(KeyError):
            p.get_pool("inst-2", "db")
