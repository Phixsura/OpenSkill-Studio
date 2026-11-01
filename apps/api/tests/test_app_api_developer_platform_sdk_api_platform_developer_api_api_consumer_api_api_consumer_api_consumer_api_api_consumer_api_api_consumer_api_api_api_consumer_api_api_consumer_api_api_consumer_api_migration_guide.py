import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_consumer_api_api_consumer_api_migration_guide import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuide, MigrationGuide, MigrationStep,
)

class TestMigrationGuide:
    def _now(self):
        return datetime(2026, 6, 1)

    def _guide(self):
        return MigrationGuide(guide_id="g1", from_version="v1", to_version="v2", title="V1 to V2 Migration", steps=[
            MigrationStep(step_id="s1", title="Update auth header", description="Change from X-API-Key to Authorization Bearer", breaking=True, order=1),
            MigrationStep(step_id="s2", title="Update response parsing", description="data field renamed", order=2),
            MigrationStep(step_id="s3", title="Test endpoints", description="Run integration tests", order=3),
        ])

    def test_create_and_progress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuide()
        svc.create_guide("inst-1", self._guide())
        progress = svc.get_progress("inst-1", "c1", "g1")
        assert progress.total_steps == 3 and progress.completed_steps == 0 and not progress.complete

    def test_complete_steps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuide()
        svc.create_guide("inst-1", self._guide())
        svc.complete_step("inst-1", "c1", "g1", "s1", self._now())
        svc.complete_step("inst-1", "c1", "g1", "s2", self._now())
        svc.complete_step("inst-1", "c1", "g1", "s3", self._now())
        progress = svc.get_progress("inst-1", "c1", "g1")
        assert progress.complete and progress.progress_pct == 100

    def test_breaking_remaining(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuide()
        svc.create_guide("inst-1", self._guide())
        progress = svc.get_progress("inst-1", "c1", "g1")
        assert progress.breaking_remaining == 1
        svc.complete_step("inst-1", "c1", "g1", "s1", self._now())
        assert svc.get_progress("inst-1", "c1", "g1").breaking_remaining == 0

    def test_empty_guide_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuide()
        with pytest.raises(ValueError, match="At least one"):
            svc.create_guide("inst-1", MigrationGuide(guide_id="g1", from_version="v1", to_version="v2", title="X"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuide()
        svc.create_guide("inst-1", self._guide())
        assert len(svc.list_guides("inst-2")) == 0
