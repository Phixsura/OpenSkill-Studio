from app.services.app_marketplace_app_app_app_app_app_app_app_ir_dashboard import incident_response_dashboard

def test_dashboard():
    r = incident_response_dashboard([
        {"id": "inc-1", "severity": "P1", "status": "active", "title": "API Down"},
        {"id": "inc-2", "severity": "P3", "status": "investigating", "title": "Slow queries"},
        {"id": "inc-3", "severity": "P4", "status": "resolved", "today": True},
    ], on_call={"primary": "alice", "secondary": "bob"})
    assert r["active_count"] == 2
    assert r["resolved_today"] == 1
    assert r["escalation_needed"]
    assert r["severity_counts"]["P1"] == 1
    assert r["on_call"]["primary"] == "alice"
