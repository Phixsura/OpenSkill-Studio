import pytest
from app.services.app_api_developer_platform_sdk_api_platform_api_consumer_migration_planner import AppAPIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlanner

class TestMigrationPlanner:
    def test_plan(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlanner()
        m = p.plan("inst-1", "c1", "v1", "v2", breaking_changes=5, estimated_effort_hours=16)
        assert m.complexity == "medium"

    def test_same_version_rejected(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlanner()
        with pytest.raises(ValueError):
            p.plan("inst-1", "c1", "v1", "v1")

    def test_blocked(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlanner()
        p.plan("inst-1", "c1", "v1", "v2")
        p.update_status("inst-1", "c1", "blocked")
        assert len(p.blocked_plans("inst-1")) == 1

    def test_pending(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlanner()
        p.plan("inst-1", "c1", "v1", "v2")
        p.plan("inst-1", "c2", "v1", "v2")
        p.update_status("inst-1", "c1", "completed")
        assert len(p.pending_plans("inst-1")) == 1

    def test_isolation(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlanner()
        p.plan("inst-1", "c1", "v1", "v2")
        assert len(p.all_plans("inst-2")) == 0
