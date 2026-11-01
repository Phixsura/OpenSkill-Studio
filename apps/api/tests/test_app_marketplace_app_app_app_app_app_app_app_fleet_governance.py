from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_governance import fleet_governance
def test_gov():
    r = fleet_governance([{"enforced": True, "last_audit_days": 30}, {"enforced": False, "last_audit_days": 100}])
    assert r["enforced"] == 1
    assert r["compliance_pct"] == 50.0
    assert not r["fully_governed"]
