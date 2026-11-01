import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_endpoint_migration_tracker import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker, MigrationTarget,
)

class TestEndpointMigrationTracker:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_add_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker()
        svc.add_migration("inst-1", "c1", MigrationTarget(old_endpoint="/v1/users", new_endpoint="/v2/users", deadline=self._now() + timedelta(days=30)))
        progress = svc.get_progress("inst-1", "c1")
        assert progress.total_count == 1 and progress.completed_count == 0

    def test_mark_completed(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker()
        svc.add_migration("inst-1", "c1", MigrationTarget(old_endpoint="/v1/users", new_endpoint="/v2/users", deadline=self._now() + timedelta(days=30)))
        svc.mark_completed("inst-1", "c1", "/v1/users")
        progress = svc.get_progress("inst-1", "c1")
        assert progress.completed_count == 1 and progress.progress_pct == 100

    def test_overdue(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker()
        svc.add_migration("inst-1", "c1", MigrationTarget(old_endpoint="/old", new_endpoint="/new", deadline=self._now()))
        overdue = svc.check_overdue("inst-1", "c1", self._now() + timedelta(days=1))
        assert len(overdue) == 1 and overdue[0].status == "overdue"

    def test_same_endpoint_rejected(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker()
        with pytest.raises(ValueError, match="must differ"):
            svc.add_migration("inst-1", "c1", MigrationTarget(old_endpoint="/api", new_endpoint="/api", deadline=self._now()))

    def test_multiple_migrations(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker()
        svc.add_migration("inst-1", "c1", MigrationTarget(old_endpoint="/v1/a", new_endpoint="/v2/a", deadline=self._now()))
        svc.add_migration("inst-1", "c1", MigrationTarget(old_endpoint="/v1/b", new_endpoint="/v2/b", deadline=self._now()))
        svc.mark_completed("inst-1", "c1", "/v1/a")
        assert svc.get_progress("inst-1", "c1").progress_pct == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointMigrationTracker()
        svc.add_migration("inst-1", "c1", MigrationTarget(old_endpoint="/old", new_endpoint="/new", deadline=self._now()))
        assert svc.get_progress("inst-2", "c1").total_count == 0
