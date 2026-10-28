"""Tests for App Deployment Tracker — lifecycle, rollback, env comparison."""

import pytest

from app.services.app_deployment_tracker import (
    AppDeploymentTracker,
    DeployStatus,
)


class TestCreateDeployment:
    def test_create(self):
        t = AppDeploymentTracker()
        d = t.create_deployment("inst-1", "dep-1", "production", "1.0.0")
        assert d.deployment_id == "dep-1"
        assert d.environment == "production"
        assert d.version == "1.0.0"
        assert d.status == DeployStatus.PENDING

    def test_missing_installation_id(self):
        t = AppDeploymentTracker()
        with pytest.raises(ValueError, match="installation_id"):
            t.create_deployment("", "dep-1", "prod", "1.0.0")

    def test_missing_version(self):
        t = AppDeploymentTracker()
        with pytest.raises(ValueError, match="version"):
            t.create_deployment("inst-1", "dep-1", "prod", "")


class TestLifecycle:
    def test_full_lifecycle(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        t.start_deployment("inst-1", "dep-1")
        d = t.complete_deployment("inst-1", "dep-1")
        assert d.status == DeployStatus.DEPLOYED

    def test_cannot_start_deployed(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        t.start_deployment("inst-1", "dep-1")
        t.complete_deployment("inst-1", "dep-1")
        with pytest.raises(ValueError, match="Cannot start"):
            t.start_deployment("inst-1", "dep-1")

    def test_cannot_complete_pending(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        with pytest.raises(ValueError, match="Cannot complete"):
            t.complete_deployment("inst-1", "dep-1")

    def test_fail_pending(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        d = t.fail_deployment("inst-1", "dep-1", error="timeout")
        assert d.status == DeployStatus.FAILED
        assert d.error_message == "timeout"

    def test_fail_deploying(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        t.start_deployment("inst-1", "dep-1")
        d = t.fail_deployment("inst-1", "dep-1")
        assert d.status == DeployStatus.FAILED

    def test_cannot_fail_deployed(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        t.start_deployment("inst-1", "dep-1")
        t.complete_deployment("inst-1", "dep-1")
        with pytest.raises(ValueError, match="Cannot fail"):
            t.fail_deployment("inst-1", "dep-1")


class TestRollback:
    def test_rollback_deployed(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "2.0.0")
        t.start_deployment("inst-1", "dep-1")
        t.complete_deployment("inst-1", "dep-1")
        d = t.rollback("inst-1", "dep-1", "1.0.0")
        assert d.status == DeployStatus.ROLLED_BACK
        assert d.rolled_back_to == "1.0.0"

    def test_cannot_rollback_pending(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "2.0.0")
        with pytest.raises(ValueError, match="Cannot roll back"):
            t.rollback("inst-1", "dep-1", "1.0.0")


class TestEnvironmentStatus:
    def test_empty_environment(self):
        t = AppDeploymentTracker()
        s = t.get_environment_status("inst-1", "prod")
        assert s.current_version is None
        assert s.deployment_count == 0

    def test_deployed_version(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        t.start_deployment("inst-1", "dep-1")
        t.complete_deployment("inst-1", "dep-1")
        s = t.get_environment_status("inst-1", "prod")
        assert s.current_version == "1.0.0"
        assert s.deployment_count == 1

    def test_rolled_back_version(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "2.0.0")
        t.start_deployment("inst-1", "dep-1")
        t.complete_deployment("inst-1", "dep-1")
        t.rollback("inst-1", "dep-1", "1.5.0")
        s = t.get_environment_status("inst-1", "prod")
        assert s.current_version == "1.5.0"

    def test_pending_no_current(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        s = t.get_environment_status("inst-1", "prod")
        assert s.current_version is None


class TestHistory:
    def test_history_order(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        t.create_deployment("inst-1", "dep-2", "prod", "2.0.0")
        h = t.list_history("inst-1", "prod")
        assert h[0].version == "2.0.0"  # newest first
        assert h[1].version == "1.0.0"

    def test_history_limit(self):
        t = AppDeploymentTracker()
        for i in range(5):
            t.create_deployment("inst-1", f"dep-{i}", "prod", f"{i}.0.0")
        h = t.list_history("inst-1", "prod", limit=3)
        assert len(h) == 3


class TestCompareEnvironments:
    def test_compare(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "staging", "2.0.0")
        t.start_deployment("inst-1", "dep-1")
        t.complete_deployment("inst-1", "dep-1")
        t.create_deployment("inst-1", "dep-2", "production", "1.0.0")
        t.start_deployment("inst-1", "dep-2")
        t.complete_deployment("inst-1", "dep-2")
        result = t.compare_environments("inst-1", ["staging", "production"])
        assert result == {"staging": "2.0.0", "production": "1.0.0"}


class TestIsolation:
    def test_different_installations(self):
        t = AppDeploymentTracker()
        t.create_deployment("inst-1", "dep-1", "prod", "1.0.0")
        with pytest.raises(KeyError):
            t.get_deployment("inst-2", "dep-1")
