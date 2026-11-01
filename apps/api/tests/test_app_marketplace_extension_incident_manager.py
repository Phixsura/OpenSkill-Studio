from app.services.app_marketplace_extension_incident_manager import (
    IncidentManagerService, IncidentSeverity, IncidentStatus,
)


def test_create_incident():
    svc = IncidentManagerService()
    inc = svc.create("ext-1", "API outage", IncidentSeverity.SEV1, affected_users=5000)
    assert inc.severity == IncidentSeverity.SEV1
    assert inc.status == IncidentStatus.OPEN
    assert len(inc.timeline) == 1


def test_assign():
    svc = IncidentManagerService()
    inc = svc.create("ext-1", "Bug", IncidentSeverity.SEV3)
    svc.assign(inc.incident_id, "alice")
    assert inc.assignee == "alice"
    assert len(inc.timeline) == 2


def test_status_updates():
    svc = IncidentManagerService()
    inc = svc.create("ext-1", "Outage", IncidentSeverity.SEV1)
    svc.update_status(inc.incident_id, IncidentStatus.INVESTIGATING, "Looking into it", "bob")
    svc.update_status(inc.incident_id, IncidentStatus.IDENTIFIED, "Found root cause", "bob")
    assert inc.status == IncidentStatus.IDENTIFIED
    assert len(inc.timeline) == 3


def test_resolve_and_mttr():
    svc = IncidentManagerService()
    inc = svc.create("ext-1", "Down", IncidentSeverity.SEV2)
    svc.update_status(inc.incident_id, IncidentStatus.RESOLVED, "Fixed", "alice")
    assert inc.status == IncidentStatus.RESOLVED
    assert inc.mttr_minutes >= 0


def test_root_cause():
    svc = IncidentManagerService()
    inc = svc.create("ext-1", "Crash", IncidentSeverity.SEV2)
    svc.set_root_cause(inc.incident_id, "Memory leak in worker process")
    assert inc.root_cause == "Memory leak in worker process"


def test_list_by_status():
    svc = IncidentManagerService()
    svc.create("ext-1", "A", IncidentSeverity.SEV3)
    inc2 = svc.create("ext-1", "B", IncidentSeverity.SEV2)
    svc.update_status(inc2.incident_id, IncidentStatus.RESOLVED, "Fixed", "x")
    open_incs = svc.list_incidents("ext-1", IncidentStatus.OPEN)
    assert len(open_incs) == 1


def test_summary():
    svc = IncidentManagerService()
    svc.create("ext-1", "A", IncidentSeverity.SEV1)
    svc.create("ext-1", "B", IncidentSeverity.SEV2)
    svc.create("ext-1", "C", IncidentSeverity.SEV2)
    summary = svc.get_summary("ext-1")
    assert summary["total"] == 3
    assert summary["by_severity"]["sev2"] == 2
    assert summary["open"] == 3
