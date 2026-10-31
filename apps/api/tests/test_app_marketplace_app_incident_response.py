from app.services.app_marketplace_app_incident_response import create_incident, add_update

def test_create():
    r = create_incident(title="API Down", severity="sev1", reported_by="alice",
        affected_services=["api", "webhooks"])
    assert r["incident_id"].startswith("INC-")
    assert r["status"] == "investigating"
    assert r["severity_label"] == "Critical"

def test_invalid_sev():
    r = create_incident(title="X", severity="sev5", reported_by="a", affected_services=[])
    assert "error" in r

def test_update():
    inc = create_incident(title="X", severity="sev2", reported_by="a", affected_services=["api"])
    r = add_update(incident=inc, message="Root cause found", status="identified", by="bob")
    assert r["status"] == "identified"
    assert len(r["timeline"]) == 2

def test_resolve():
    inc = create_incident(title="X", severity="sev3", reported_by="a", affected_services=[])
    r = add_update(incident=inc, message="Fixed", status="resolved", by="bob")
    assert r["status"] == "resolved"
    assert r["resolved_at"] is not None
