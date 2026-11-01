"""Tests for App Deployment History — start, finish, success rate."""

import pytest

from app.services.app_deployment_history import AppDeploymentHistory, DeployResult


class TestStart:
    def test_start(self):
        h = AppDeploymentHistory()
        d = h.start("inst-1", "d1", "v2.0", "abc123", "alice")
        assert d.result == DeployResult.IN_PROGRESS


class TestFinish:
    def test_success(self):
        h = AppDeploymentHistory()
        h.start("inst-1", "d1", "v2.0", "abc123", "alice")
        d = h.finish("inst-1", "d1", DeployResult.SUCCESS)
        assert d.duration_seconds is not None

    def test_failure(self):
        h = AppDeploymentHistory()
        h.start("inst-1", "d1", "v2.0", "abc123", "alice")
        d = h.finish("inst-1", "d1", DeployResult.FAILURE, "OOM")
        assert d.error == "OOM"


class TestQuery:
    def test_recent(self):
        h = AppDeploymentHistory()
        for i in range(5):
            h.start("inst-1", f"d{i}", f"v{i}", f"sha{i}", "alice")
        recent = h.recent("inst-1", limit=3)
        assert len(recent) == 3
        assert recent[0].deploy_id == "d4"

    def test_success_rate(self):
        h = AppDeploymentHistory()
        for i in range(4):
            h.start("inst-1", f"d{i}", f"v{i}", f"sha{i}", "alice")
            h.finish("inst-1", f"d{i}", DeployResult.SUCCESS)
        h.start("inst-1", "d4", "v4", "sha4", "alice")
        h.finish("inst-1", "d4", DeployResult.FAILURE)
        assert h.success_rate("inst-1") == 80.0


class TestIsolation:
    def test_cross(self):
        h = AppDeploymentHistory()
        h.start("inst-1", "d1", "v1", "sha", "alice")
        assert h.count("inst-2") == 0
