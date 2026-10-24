from app.services.app_marketplace_app_app_app_app_app_app_app_severity_class import classify_severity, severity_distribution

def test_p1():
    r = classify_severity({"data_loss": True, "affected_users": 100, "services_down": 1})
    assert r["severity"] == "P1"
    assert r["response_time"] == "15 minutes"

def test_p2():
    r = classify_severity({"affected_users": 5000, "revenue_impact_per_hour": 5000, "services_down": 1})
    assert r["severity"] == "P2"

def test_p4():
    r = classify_severity({"affected_users": 5, "services_down": 0})
    assert r["severity"] == "P4"

def test_distribution():
    r = severity_distribution([{"severity": "P1"}, {"severity": "P2"}, {"severity": "P2"}])
    assert r["distribution"]["P1"] == 1
    assert r["distribution"]["P2"] == 2
