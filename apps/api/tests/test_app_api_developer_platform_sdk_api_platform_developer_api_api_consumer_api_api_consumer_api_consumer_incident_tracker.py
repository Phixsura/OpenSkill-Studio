import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_incident_tracker import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker, Incident, IncidentUpdate,
)

class TestConsumerIncidentTracker:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker()
        svc.create("inst-1", Incident(incident_id="i1", title="DB Outage", severity="critical", created_at=self._now()))
        assert svc.get("inst-1", "i1").title == "DB Outage"

    def test_update_and_resolve(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker()
        svc.create("inst-1", Incident(incident_id="i1", title="Slow API", severity="minor", created_at=self._now()))
        svc.update_status("inst-1", "i1", IncidentUpdate(update_id="u1", incident_id="i1", message="Fix deployed", status="resolved", timestamp=self._now()))
        assert svc.get("inst-1", "i1").status == "resolved"

    def test_cannot_update_resolved(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker()
        svc.create("inst-1", Incident(incident_id="i1", title="X", severity="minor", created_at=self._now()))
        svc.update_status("inst-1", "i1", IncidentUpdate(update_id="u1", incident_id="i1", message="Done", status="resolved", timestamp=self._now()))
        with pytest.raises(ValueError, match="resolved"):
            svc.update_status("inst-1", "i1", IncidentUpdate(update_id="u2", incident_id="i1", message="Oops", status="investigating", timestamp=self._now()))

    def test_active_sorted_by_severity(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker()
        svc.create("inst-1", Incident(incident_id="i1", title="Minor", severity="minor", created_at=self._now()))
        svc.create("inst-1", Incident(incident_id="i2", title="Critical", severity="critical", created_at=self._now()))
        active = svc.active_incidents("inst-1")
        assert active[0].severity == "critical"

    def test_consumer_filter(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker()
        svc.create("inst-1", Incident(incident_id="i1", title="All", severity="minor", affected_consumers=[], created_at=self._now()))
        svc.create("inst-1", Incident(incident_id="i2", title="C1 only", severity="minor", affected_consumers=["c1"], created_at=self._now()))
        assert len(svc.active_incidents("inst-1", consumer_id="c2")) == 1  # only the "all" incident

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker()
        svc.create("inst-1", Incident(incident_id="i1", title="X", severity="minor", created_at=self._now()))
        assert len(svc.active_incidents("inst-2")) == 0
