from app.services.app_marketplace_app_app_app_app_app_app_app_incident_commander import IncidentCommander

def test_incident():
    ic = IncidentCommander()
    inc = ic.declare(title="DB Outage", severity="sev1", commander="alice",
                      affected_services=["database", "api"])
    assert inc["status"] == "investigating"
    ic.update_status(inc["id"], status="identified", note="Disk full", by="alice")
    ic.resolve(inc["id"], resolution="Expanded disk and restarted", by="alice")
    ic.add_postmortem(inc["id"], summary="DB ran out of disk",
                       root_cause="No disk space alerts",
                       action_items=["Add disk monitoring", "Set up auto-expand"])
    incs = ic.list_incidents()
    assert len(incs) == 1
    assert incs[0]["status"] == "resolved"
    assert incs[0]["events"] == 3
