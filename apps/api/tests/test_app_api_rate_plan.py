"""Tests for App API Rate Plan — create, assign, check limits."""

import pytest

from app.services.app_api_rate_plan import AppAPIRatePlan


class TestCreate:
    def test_create(self):
        r = AppAPIRatePlan()
        p = r.create_plan("inst-1", "free", "Free", rpm=60, rph=1000, rpd=10000)
        assert p.requests_per_minute == 60

    def test_negative(self):
        r = AppAPIRatePlan()
        with pytest.raises(ValueError):
            r.create_plan("inst-1", "bad", "Bad", rpm=-1, rph=0, rpd=0)


class TestAssign:
    def test_assign(self):
        r = AppAPIRatePlan()
        r.create_plan("inst-1", "free", "Free", rpm=60, rph=1000, rpd=10000)
        r.assign_plan("inst-1", "tenant-1", "free")
        p = r.tenant_plan("inst-1", "tenant-1")
        assert p is not None
        assert p.name == "Free"

    def test_invalid_plan(self):
        r = AppAPIRatePlan()
        with pytest.raises(KeyError):
            r.assign_plan("inst-1", "tenant-1", "nonexistent")


class TestCheck:
    def test_under_limit(self):
        r = AppAPIRatePlan()
        r.create_plan("inst-1", "free", "Free", rpm=10, rph=100, rpd=1000)
        r.assign_plan("inst-1", "t1", "free")
        result = r.check_limit("inst-1", "t1")
        assert result["allowed"] is True

    def test_over_limit(self):
        r = AppAPIRatePlan()
        r.create_plan("inst-1", "strict", "Strict", rpm=2, rph=100, rpd=1000)
        r.assign_plan("inst-1", "t1", "strict")
        for _ in range(3):
            r.record_request("inst-1", "t1")
        result = r.check_limit("inst-1", "t1")
        assert result["allowed"] is False

    def test_no_plan(self):
        r = AppAPIRatePlan()
        result = r.check_limit("inst-1", "t1")
        assert result["allowed"] is True


class TestIsolation:
    def test_cross(self):
        r = AppAPIRatePlan()
        r.create_plan("inst-1", "free", "Free", rpm=60, rph=1000, rpd=10000)
        assert r.list_plans("inst-2") == []
