from app.services.app_marketplace_incident_report import create_incident, add_update, compute_uptime

def test_create():
    r = create_incident(app_id="a1", title="API Down", severity="critical", description="500 errors")
    assert r["status"] == "investigating"

def test_invalid_severity():
    r = create_incident(app_id="a1", title="X", severity="low", description="D")
    assert r["error"]

def test_update():
    inc = {"title": "Down", "status": "investigating", "updates": []}
    r = add_update(incident=inc, message="Found root cause", new_status="identified")
    assert r["status"] == "identified"
    assert len(r["updates"]) == 1

def test_uptime():
    incidents = [{"downtime_hours": 2}, {"downtime_hours": 1}]
    u = compute_uptime(incidents=incidents)
    assert u["uptime_pct"] > 99
    assert u["incidents"] == 2
