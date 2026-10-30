import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_migration_status import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatus, MigrationState,
)

class TestConsumerApiMigrationStatus:
    def test_start_migration(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatus()
        ms = svc.start_migration("inst-1", "c1", "v1", "v2")
        assert ms.state == MigrationState.IN_PROGRESS

    def test_complete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatus()
        svc.start_migration("inst-1", "c1", "v1", "v2")
        svc.update_progress("inst-1", "c1", 50.0)
        ms = svc.complete("inst-1", "c1")
        assert ms.state == MigrationState.COMPLETED and ms.progress_pct == 100.0

    def test_rollback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatus()
        svc.start_migration("inst-1", "c1", "v1", "v2")
        ms = svc.rollback("inst-1", "c1")
        assert ms.state == MigrationState.ROLLED_BACK

    def test_duplicate_migration(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatus()
        svc.start_migration("inst-1", "c1", "v1", "v2")
        with pytest.raises(ValueError, match="already in progress"):
            svc.start_migration("inst-1", "c1", "v1", "v2")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiMigrationStatus()
        svc.start_migration("inst-1", "c1", "v1", "v2")
        assert len(svc.list_migrations("inst-2")) == 0
