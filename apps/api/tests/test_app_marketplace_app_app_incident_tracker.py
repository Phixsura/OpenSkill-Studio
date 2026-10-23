from app.services.app_marketplace_app_app_incident_tracker import create_incident, update_status, build_incident_dashboard

def test_create():
    r = create_incident(title="API outage", severity="sev1")
    assert r["id"].startswith("INC-")
    assert r["status"] == "investigating"
    assert r["severity_label"] == "Critical"
    assert len(r["timeline"]) == 1

def test_update():
    inc = create_incident(title="Slow queries", severity="sev3")
    r = update_status(incident=inc, status="identified", message="Found slow query")
    assert r["status"] == "identified"
    assert len(r["timeline"]) == 2

def test_resolve():
    inc = create_incident(title="Test")
    update_status(incident=inc, status="resolved", message="Fixed")
    assert "resolved_at" in inc

def test_dashboard():
    incs = [
        create_incident(title="A", severity="sev1"),
        create_incident(title="B", severity="sev3"),
    ]
    update_status(incident=incs[1], status="resolved")
    r = build_incident_dashboard(incidents=incs)
    assert r["active"] == 1
    assert r["has_critical"]
