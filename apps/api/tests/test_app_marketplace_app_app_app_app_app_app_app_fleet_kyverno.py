from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kyverno import fleet_kyverno_status
def test_ky():
    r = fleet_kyverno_status([{"mode": "enforce", "violations": 0}, {"mode": "audit", "violations": 5}])
    assert r["enforcing"] == 1
    assert r["violations"] == 5
    assert not r["compliant"]
