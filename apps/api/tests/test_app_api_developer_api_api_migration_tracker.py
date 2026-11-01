import pytest
from app.services.app_api_developer_api_api_migration_tracker import AppAPIDeveloperAPIApiMigrationTracker

class TestMigrationTracker:
    def test_create(self):
        t = AppAPIDeveloperAPIApiMigrationTracker()
        m = t.create("inst-1", "t1", "c1", "v1", "v2")
        assert m.status == "pending"

    def test_same_version_rejected(self):
        t = AppAPIDeveloperAPIApiMigrationTracker()
        with pytest.raises(ValueError):
            t.create("inst-1", "t1", "c1", "v1", "v1")

    def test_lifecycle(self):
        t = AppAPIDeveloperAPIApiMigrationTracker()
        t.create("inst-1", "t1", "c1", "v1", "v2")
        t.start("inst-1", "t1")
        m = t.complete("inst-1", "t1", "Migration successful")
        assert m.status == "completed"
        assert m.completed_at is not None

    def test_progress(self):
        t = AppAPIDeveloperAPIApiMigrationTracker()
        t.create("inst-1", "t1", "c1", "v1", "v2")
        t.create("inst-1", "t2", "c2", "v1", "v2")
        t.complete("inst-1", "t1")
        p = t.progress("inst-1")
        assert p["completed"] == 1
        assert p["pending"] == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiMigrationTracker()
        t.create("inst-1", "t1", "c1", "v1", "v2")
        assert len(t.pending("inst-2")) == 0
