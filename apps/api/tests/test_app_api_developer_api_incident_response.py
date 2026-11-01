import pytest
from app.services.app_api_developer_api_incident_response import AppAPIDeveloperAPIIncidentResponse, ResponseStatus

class TestResponse:
    def test_create(self):
        r = AppAPIDeveloperAPIIncidentResponse()
        ir = r.create("inst-1", "r1", "api_outage", ["Assess", "Mitigate", "Recover"], ["alice", "bob"])
        assert ir.status == ResponseStatus.IDLE
        assert len(ir.playbook_steps) == 3

    def test_lifecycle(self):
        r = AppAPIDeveloperAPIIncidentResponse()
        r.create("inst-1", "r1", "outage", ["Step1", "Step2", "Step3"])
        r.activate("inst-1", "r1")
        r.advance_step("inst-1", "r1")
        r.advance_step("inst-1", "r1")
        ir = r.advance_step("inst-1", "r1")  # last step → resolved
        assert ir.status == ResponseStatus.RESOLVED

    def test_active(self):
        r = AppAPIDeveloperAPIIncidentResponse()
        r.create("inst-1", "r1", "outage", ["S1"])
        r.activate("inst-1", "r1")
        assert len(r.active_responses("inst-1")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIIncidentResponse()
        r.create("inst-1", "r1", "outage", ["S1"])
        assert r.list_responses("inst-2") == []
