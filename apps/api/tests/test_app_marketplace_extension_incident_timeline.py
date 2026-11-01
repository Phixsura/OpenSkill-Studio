from app.services.app_marketplace_extension_incident_timeline import IncidentTimelineService

def test_create_and_update():
    svc = IncidentTimelineService()
    inc = svc.create("API Latency Spike", "major")
    assert len(inc.events) == 1
    evt = svc.add_update(inc.incident_id, "identified", "Root cause found")
    assert evt is not None
    assert len(svc.get_active()) == 1

def test_resolve():
    svc = IncidentTimelineService()
    inc = svc.create("DB Connection Issue", "critical")
    svc.add_update(inc.incident_id, "resolved", "Fixed connection pool")
    assert len(svc.get_active()) == 0
    assert svc.get_history()[0].resolved is True

def test_no_update_after_resolve():
    svc = IncidentTimelineService()
    inc = svc.create("Issue", "minor")
    svc.add_update(inc.incident_id, "resolved", "Done")
    assert svc.add_update(inc.incident_id, "monitoring", "Check") is None
