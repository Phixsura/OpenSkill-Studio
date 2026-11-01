import time, pytest
from app.services.app_api_developer_api_incident_tracker import AppAPIDeveloperAPIIncidentTracker

class TestIncidentTracker:
    def test_create(self):
        t = AppAPIDeveloperAPIIncidentTracker()
        i = t.create("inst-1", "inc-1", "API down", "critical", ["/api/users"])
        assert i.severity == "critical"
        assert i.status == "open"

    def test_invalid_severity(self):
        t = AppAPIDeveloperAPIIncidentTracker()
        with pytest.raises(ValueError):
            t.create("inst-1", "inc-1", "test", "unknown")

    def test_resolve(self):
        t = AppAPIDeveloperAPIIncidentTracker()
        t.create("inst-1", "inc-1", "Slow API", "minor")
        i = t.update_status("inst-1", "inc-1", "resolved", root_cause="DB connection pool")
        assert i.status == "resolved"
        assert i.root_cause == "DB connection pool"

    def test_open_incidents(self):
        t = AppAPIDeveloperAPIIncidentTracker()
        t.create("inst-1", "inc-1", "A", "major")
        t.create("inst-1", "inc-2", "B", "minor")
        t.update_status("inst-1", "inc-2", "resolved")
        assert len(t.open_incidents("inst-1")) == 1

    def test_isolation(self):
        t = AppAPIDeveloperAPIIncidentTracker()
        t.create("inst-1", "inc-1", "A", "major")
        assert len(t.open_incidents("inst-2")) == 0
