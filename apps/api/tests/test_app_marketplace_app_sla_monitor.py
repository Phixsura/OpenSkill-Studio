from app.services.app_marketplace_app_sla_monitor import define_sla, check_sla_compliance, calculate_sla_credits

def test_define():
    s = define_sla(app_id="a1", uptime_target=99.9, response_time_target_ms=200, support_response_hours=4)
    assert s["uptime_target"] == 99.9

def test_define_invalid():
    s = define_sla(app_id="a1", uptime_target=50, response_time_target_ms=200, support_response_hours=4)
    assert s["error"]

def test_compliant():
    sla = {"uptime_target": 99.9, "response_time_target_ms": 200, "support_response_hours": 4}
    r = check_sla_compliance(sla=sla, actual_uptime=99.95, actual_response_ms=150, actual_support_hours=2)
    assert r["compliant"]

def test_not_compliant():
    sla = {"uptime_target": 99.9, "response_time_target_ms": 200, "support_response_hours": 4}
    r = check_sla_compliance(sla=sla, actual_uptime=99.5, actual_response_ms=300, actual_support_hours=6)
    assert not r["compliant"]

def test_credits():
    sla = {"uptime_target": 99.9}
    c = calculate_sla_credits(sla=sla, actual_uptime=99.0, monthly_fee=10000)
    assert c["credit_pct"] == 9
    assert c["credit_amount"] == 900

def test_no_credits():
    sla = {"uptime_target": 99.9}
    c = calculate_sla_credits(sla=sla, actual_uptime=99.99, monthly_fee=10000)
    assert c["credit_amount"] == 0
