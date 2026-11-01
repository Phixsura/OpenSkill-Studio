from app.services.app_marketplace_app_app_app_app_app_app_app_incident_resp import (
    create_incident, assign_responder, update_status, incident_metrics,
)

def test_workflow():
    inc = create_incident("DB Outage", "critical", "alice", ["database", "api"])
    assert inc["status"] == "investigating"
    assign_responder(inc, "bob")
    assert len(inc["responders"]) == 2
    update_status(inc, "identified", "bob")
    assert inc["status"] == "identified"
    update_status(inc, "resolved", "alice")
    assert inc["status"] == "resolved"
    assert len(inc["timeline"]) == 4

def test_metrics():
    incidents = [
        {"severity": "critical", "status": "resolved"},
        {"severity": "major", "status": "investigating"},
        {"severity": "critical", "status": "resolved"},
    ]
    r = incident_metrics(incidents)
    assert r["resolved"] == 2
    assert r["open"] == 1
    assert r["by_severity"]["critical"] == 2
