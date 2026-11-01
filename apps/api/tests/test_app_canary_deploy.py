"""Tests for App Canary Deploy — progressive traffic shifting."""

import pytest

from app.services.app_canary_deploy import AppCanaryDeploy, DeployStatus

STAGES = [
    {"stage_id": "s1", "traffic_pct": 5, "duration_seconds": 60, "health_threshold": 0.95},
    {"stage_id": "s2", "traffic_pct": 25, "duration_seconds": 120},
    {"stage_id": "s3", "traffic_pct": 100, "duration_seconds": 300},
]


class TestCreate:
    def test_create(self):
        c = AppCanaryDeploy()
        d = c.create_deploy("inst-1", "d1", "v2.0", STAGES)
        assert len(d.stages) == 3
        assert d.status == DeployStatus.PENDING

    def test_ascending_required(self):
        c = AppCanaryDeploy()
        bad = [{"stage_id": "a", "traffic_pct": 50}, {"stage_id": "b", "traffic_pct": 10}]
        with pytest.raises(ValueError, match="ascending"):
            c.create_deploy("inst-1", "d1", "v1", bad)

    def test_invalid_pct(self):
        c = AppCanaryDeploy()
        with pytest.raises(ValueError):
            c.create_deploy("inst-1", "d1", "v1", [{"stage_id": "a", "traffic_pct": 0}])


class TestLifecycle:
    def test_start_and_advance(self):
        c = AppCanaryDeploy()
        c.create_deploy("inst-1", "d1", "v2.0", STAGES)
        c.start("inst-1", "d1")
        assert c.current_traffic("inst-1", "d1") == 5

        c.report_health("inst-1", "d1", 0.99)
        c.advance("inst-1", "d1")
        assert c.current_traffic("inst-1", "d1") == 25

    def test_complete(self):
        c = AppCanaryDeploy()
        c.create_deploy("inst-1", "d1", "v2.0", STAGES)
        c.start("inst-1", "d1")
        for _ in range(3):
            c.report_health("inst-1", "d1", 0.99)
            c.advance("inst-1", "d1")
        assert c.get_deploy("inst-1", "d1").status == DeployStatus.COMPLETED

    def test_cannot_advance_unhealthy(self):
        c = AppCanaryDeploy()
        c.create_deploy("inst-1", "d1", "v2.0", STAGES)
        c.start("inst-1", "d1")
        c.report_health("inst-1", "d1", 0.5)
        with pytest.raises(ValueError, match="not healthy"):
            c.advance("inst-1", "d1")


class TestRollback:
    def test_rollback(self):
        c = AppCanaryDeploy()
        c.create_deploy("inst-1", "d1", "v2.0", STAGES)
        c.start("inst-1", "d1")
        c.rollback("inst-1", "d1", "error spike")
        assert c.get_deploy("inst-1", "d1").status == DeployStatus.ROLLED_BACK

    def test_rollback_completed_fails(self):
        c = AppCanaryDeploy()
        c.create_deploy("inst-1", "d1", "v2.0", STAGES)
        c.start("inst-1", "d1")
        for _ in range(3):
            c.report_health("inst-1", "d1", 0.99)
            c.advance("inst-1", "d1")
        with pytest.raises(ValueError):
            c.rollback("inst-1", "d1")


class TestIsolation:
    def test_cross(self):
        c = AppCanaryDeploy()
        c.create_deploy("inst-1", "d1", "v2.0", STAGES)
        assert c.list_deploys("inst-2") == []
