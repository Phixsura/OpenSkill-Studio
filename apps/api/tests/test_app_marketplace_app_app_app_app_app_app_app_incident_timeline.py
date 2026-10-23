from app.services.app_marketplace_app_app_app_app_app_app_app_incident_timeline import build_incident, summarize_incidents

def test_build():
    r = build_incident("DB Down", "critical", [
        {"type": "triggered", "timestamp": 1000},
        {"type": "acknowledged", "timestamp": 1060},
        {"type": "resolved", "timestamp": 1600},
    ])
    assert r["status"] == "resolved"
    assert r["severity_level"] == 1
    assert r["duration_min"] == 10

def test_summarize():
    r = summarize_incidents([
        {"severity": "critical", "status": "resolved"},
        {"severity": "major", "status": "open"},
        {"severity": "critical", "status": "open"},
    ])
    assert r["total"] == 3
    assert r["open"] == 2
    assert r["by_severity"]["critical"] == 2
