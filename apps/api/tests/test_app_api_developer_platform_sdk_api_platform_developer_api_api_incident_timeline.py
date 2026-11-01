import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_incident_timeline import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimeline, IncidentSeverity, IncidentPhase,
)

class TestApiIncidentTimeline:
    def test_create_incident(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimeline()
        ir = svc.create_incident("inst-1", "inc-1", "DB outage", IncidentSeverity.CRITICAL, ["/api/users"])
        assert ir.current_phase == IncidentPhase.DETECTED
        assert len(ir.timeline) == 1

    def test_phase_progression(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimeline()
        svc.create_incident("inst-1", "inc-1", "Slow API", IncidentSeverity.MAJOR)
        svc.update_phase("inst-1", "inc-1", IncidentPhase.INVESTIGATING, "Looking into it")
        svc.update_phase("inst-1", "inc-1", IncidentPhase.RESOLVED, "Fixed")
        ir = svc.get_incident("inst-1", "inc-1")
        assert ir.current_phase == IncidentPhase.RESOLVED
        assert ir.duration_minutes >= 0
        assert len(ir.timeline) == 3

    def test_no_backward_phase(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimeline()
        svc.create_incident("inst-1", "inc-1", "Test", IncidentSeverity.MINOR)
        svc.update_phase("inst-1", "inc-1", IncidentPhase.MONITORING, "Watching")
        with pytest.raises(ValueError, match="backwards"):
            svc.update_phase("inst-1", "inc-1", IncidentPhase.INVESTIGATING, "Oops")

    def test_active_vs_resolved(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimeline()
        svc.create_incident("inst-1", "inc-1", "Active", IncidentSeverity.MINOR)
        svc.create_incident("inst-1", "inc-2", "Done", IncidentSeverity.MINOR)
        svc.update_phase("inst-1", "inc-2", IncidentPhase.RESOLVED, "Fixed")
        assert len(svc.active_incidents("inst-1")) == 1
        assert len(svc.resolved_incidents("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimeline()
        svc.create_incident("inst-1", "inc-1", "Test", IncidentSeverity.MINOR)
        assert len(svc.active_incidents("inst-2")) == 0
