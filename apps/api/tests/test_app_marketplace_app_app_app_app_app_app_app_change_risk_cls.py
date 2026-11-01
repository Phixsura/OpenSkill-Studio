from app.services.app_marketplace_app_app_app_app_app_app_app_change_risk_cls import classify_change_risk

def test_critical():
    r = classify_change_risk({"type": "endpoint_removal", "affects_auth": True, "consumers": 100})
    assert r["level"] == "critical"
    assert "breaking" in r["tags"]

def test_low():
    r = classify_change_risk({"type": "new_endpoint", "consumers": 0})
    assert r["level"] == "low"
    assert "additive" in r["tags"]
