"""Tests for Endpoint Deprecation Planner service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_deprecation_planner import DeprecationPlanner


class TestDeprecationPlanner:
    def test_create_plan(self):
        svc = DeprecationPlanner()
        result = svc.create_plan("dp1", "/v1/users", "/v2/users",
                                  "2024-01-01", "2024-06-01", ["c1", "c2"])
        assert result["affected_consumers"] == 2

    def test_advance_phase(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/old", "/new", "2024-01", "2024-06")
        result = svc.advance_phase("dp1")
        assert result["phase"] == "warning"
        svc.advance_phase("dp1")
        assert svc.get_plan("dp1")["phase"] == "migration"

    def test_mark_migrated(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/old", "/new", "2024-01", "2024-06", ["c1", "c2"])
        result = svc.mark_migrated("dp1", "c1")
        assert result["migrated"] is True
        assert result["remaining"] == 1
        assert result["migration_pct"] == 50.0

    def test_ready_to_sunset(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/old", "/new", "2024-01", "2024-06", ["c1"])
        svc.mark_migrated("dp1", "c1")
        plan = svc.get_plan("dp1")
        assert plan["ready_to_sunset"] is True

    def test_consumer_migrations(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/v1", "/v2", "2024-01", "2024-06", ["c1"])
        svc.create_plan("dp2", "/v2", "/v3", "2024-07", "2024-12", ["c1"])
        svc.mark_migrated("dp1", "c1")
        migrations = svc.get_consumer_migrations("c1")
        assert len(migrations) == 2
        statuses = {m["plan_id"]: m["status"] for m in migrations}
        assert statuses["dp1"] == "migrated"
        assert statuses["dp2"] == "pending"

    def test_list_by_phase(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/a", "/b", "2024-01", "2024-06")
        svc.create_plan("dp2", "/c", "/d", "2024-01", "2024-06")
        svc.advance_phase("dp2")
        announced = svc.list_plans(phase="announced")
        assert len(announced) == 1

    def test_stats(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/a", "/b", "2024-01", "2024-06", ["c1", "c2"])
        stats = svc.get_stats()
        assert stats["total_plans"] == 1
        assert stats["consumers_pending_migration"] == 2

    def test_final_phase_error(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/a", "/b", "2024-01", "2024-06")
        for _ in range(4):
            svc.advance_phase("dp1")
        with pytest.raises(ValueError):
            svc.advance_phase("dp1")

    def test_duplicate_plan(self):
        svc = DeprecationPlanner()
        svc.create_plan("dp1", "/a", "/b", "2024-01", "2024-06")
        with pytest.raises(ValueError):
            svc.create_plan("dp1", "/c", "/d", "2024-01", "2024-06")

    def test_isolation(self):
        a, b = DeprecationPlanner(), DeprecationPlanner()
        a.create_plan("dp1", "/a", "/b", "2024-01", "2024-06")
        assert b.get_plan("dp1") is None
