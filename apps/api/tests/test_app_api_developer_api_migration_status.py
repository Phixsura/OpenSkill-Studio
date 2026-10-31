from app.services.app_api_developer_api_migration_status import AppAPIDeveloperAPIMigrationStatus

class TestMigration:
    def test_track(self):
        m = AppAPIDeveloperAPIMigrationStatus()
        cm = m.track("inst-1", "app-1", "v1", "v2")
        assert cm.migrated is False

    def test_progress(self):
        m = AppAPIDeveloperAPIMigrationStatus()
        m.track("inst-1", "app-1", "v1", "v2")
        m.track("inst-1", "app-2", "v1", "v2")
        m.mark_migrated("inst-1", "app-1")
        p = m.migration_progress("inst-1")
        assert p["pct"] == 50.0

    def test_not_migrated(self):
        m = AppAPIDeveloperAPIMigrationStatus()
        m.track("inst-1", "app-1", "v1", "v2")
        m.track("inst-1", "app-2", "v1", "v2")
        m.mark_migrated("inst-1", "app-1")
        assert len(m.not_migrated("inst-1")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperAPIMigrationStatus()
        m.track("inst-1", "app-1", "v1", "v2")
        assert m.list_all("inst-2") == []
