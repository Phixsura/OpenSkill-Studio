import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_incident_response import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponse

class TestIncidentResponse:
    def test_declare(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponse()
        i = r.declare("inst-1", "i1", "DB Outage", "sev1", "alice", ["database", "api"])
        assert i.status == "detected"
        assert len(i.affected_services) == 2

    def test_advance(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponse()
        r.declare("inst-1", "i1", "Outage", "sev1", "alice")
        r.advance("inst-1", "i1")
        assert r.all_incidents("inst-1")[0].status == "triaging"

    def test_full_lifecycle(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponse()
        r.declare("inst-1", "i1", "Outage", "sev2", "bob")
        for _ in range(4): r.advance("inst-1", "i1")
        i = r.all_incidents("inst-1")[0]
        assert i.resolved is True

    def test_active(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponse()
        r.declare("inst-1", "i1", "A", "sev1", "alice")
        r.declare("inst-1", "i2", "B", "sev2", "bob")
        for _ in range(4): r.advance("inst-1", "i1")
        assert len(r.active_incidents("inst-1")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponse()
        r.declare("inst-1", "i1", "X", "sev1", "alice")
        assert len(r.all_incidents("inst-2")) == 0
