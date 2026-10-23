from app.services.app_marketplace_app_app_app_app_app_app_app_sla_tracker import check_sla_compliance

def test_compliant():
    r = check_sla_compliance(uptime_pct=99.95, avg_response_ms=150,
                              p99_response_ms=800, incidents=1)
    assert r["compliant"]
    assert r["status"] == "compliant"
    assert r["score"] == 100
    assert not r["credit_due"]

def test_breached():
    r = check_sla_compliance(uptime_pct=99.5, avg_response_ms=350,
                              p99_response_ms=1500, incidents=5)
    assert not r["compliant"]
    assert r["status"] == "breached"
    assert r["credit_due"]
    assert r["passed"] == 0
