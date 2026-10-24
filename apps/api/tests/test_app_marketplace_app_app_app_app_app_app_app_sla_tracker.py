from app.services.app_marketplace_app_app_app_app_app_app_app_sla_tracker import check_sla, fleet_sla

def test_compliant():
    r = check_sla("api", 99.99, 99.9, 150, 200)
    assert r["compliant"]

def test_non_compliant():
    r = check_sla("api", 99.5, 99.9, 250, 200)
    assert not r["compliant"]

def test_fleet():
    svcs = [check_sla("a", 99.99, 99.9, 100, 200), check_sla("b", 99.0, 99.9, 100, 200)]
    r = fleet_sla(svcs)
    assert r["compliant"] == 1
    assert r["compliance_pct"] == 50.0
