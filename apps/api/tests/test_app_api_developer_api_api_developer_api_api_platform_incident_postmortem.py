import pytest
from app.services.app_api_developer_api_api_developer_api_api_platform_incident_postmortem import AppAPIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortem

class TestIncidentPostmortem:
    def test_create(self):
        pm = AppAPIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortem()
        p = pm.create("inst-1", "pm1", "inc-1", "DB Outage", "sev1", "Connection pool exhausted", "API down for 30min", action_items=["Add connection pooling alerts"], duration_minutes=30)
        assert p.severity == "sev1"

    def test_publish_requires_actions(self):
        pm = AppAPIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortem()
        pm.create("inst-1", "pm1", "inc-1", "Outage", "sev2", "Bug", "Impact")
        with pytest.raises(ValueError, match="action items"):
            pm.publish("inst-1", "pm1")

    def test_publish_with_actions(self):
        pm = AppAPIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortem()
        pm.create("inst-1", "pm1", "inc-1", "Outage", "sev2", "Bug", "Impact", action_items=["Fix it"])
        p = pm.publish("inst-1", "pm1")
        assert p.status == "published"

    def test_by_severity(self):
        pm = AppAPIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortem()
        pm.create("inst-1", "pm1", "i1", "A", "sev1", "x", "y", action_items=["a"])
        pm.create("inst-1", "pm2", "i2", "B", "sev3", "x", "y", action_items=["b"])
        assert pm.by_severity("inst-1") == {"sev1": 1, "sev3": 1}

    def test_isolation(self):
        pm = AppAPIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortem()
        pm.create("inst-1", "pm1", "i1", "A", "sev1", "x", "y")
        assert len(pm.all_postmortems("inst-2")) == 0
