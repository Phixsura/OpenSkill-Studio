from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_migration_guide import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMigrationGuide, MigrationGuide, MigrationStep,
)

class TestMigrationGuide:
    def test_create_with_hours(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMigrationGuide()
        steps = [MigrationStep(step_id="s1", title="Update auth", description="Switch to OAuth2", difficulty="medium", breaking=True), MigrationStep(step_id="s2", title="Rename field", description="name→full_name", difficulty="easy")]
        g = svc.create_guide("inst-1", MigrationGuide(guide_id="g1", from_version="v1", to_version="v2", steps=steps))
        assert g.estimated_hours == 2.5  # 2.0 + 0.5

    def test_find_by_versions(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMigrationGuide()
        svc.create_guide("inst-1", MigrationGuide(guide_id="g1", from_version="v1", to_version="v2", steps=[MigrationStep(step_id="s1", title="X", description="Y")]))
        g = svc.get_guide("inst-1", "v1", "v2")
        assert g is not None

    def test_breaking_steps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMigrationGuide()
        steps = [MigrationStep(step_id="s1", title="A", description="B", breaking=True), MigrationStep(step_id="s2", title="C", description="D")]
        svc.create_guide("inst-1", MigrationGuide(guide_id="g1", from_version="v1", to_version="v2", steps=steps))
        assert len(svc.breaking_steps("inst-1", "g1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMigrationGuide()
        svc.create_guide("inst-1", MigrationGuide(guide_id="g1", from_version="v1", to_version="v2", steps=[MigrationStep(step_id="s1", title="X", description="Y")]))
        assert len(svc.list_guides("inst-2")) == 0
