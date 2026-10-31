from app.services.app_marketplace_incident_timeline import build_incident_timeline

def test_timeline():
    r = build_incident_timeline(days=90)
    assert r["total_incidents"] == 3
    assert r["uptime_pct"] > 99.0
    assert r["mttr_min"] > 0
    assert r["incidents"][0]["severity"] == "minor"

def test_period():
    r = build_incident_timeline(days=30)
    assert r["period_days"] == 30
