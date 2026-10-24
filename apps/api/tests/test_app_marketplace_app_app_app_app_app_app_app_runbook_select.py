from app.services.app_marketplace_app_app_app_app_app_app_app_runbook_select import select_runbook

def test_select():
    r = select_runbook(
        {"service": "api", "type": "high_error_rate", "severity": "P1", "tags": ["backend"]},
        [{"name": "restart_api", "services": ["api"], "incident_types": ["high_error_rate"],
          "severities": ["P1", "P2"], "tags": ["backend"], "steps": 5},
         {"name": "scale_up", "services": ["api"], "incident_types": ["high_latency"],
          "severities": ["P1"], "tags": [], "steps": 3}])
    assert r["selected"] == "restart_api"
    assert r["confidence"] >= 10

def test_no_match():
    r = select_runbook({"service": "unknown", "type": "weird"}, [])
    assert r["selected"] is None
