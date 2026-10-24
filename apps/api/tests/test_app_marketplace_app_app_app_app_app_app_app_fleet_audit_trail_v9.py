from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_audit_trail_v9 import fleet_audit_trail_v9
def test_audit_v9():
    r = fleet_audit_trail_v9([{"severity": "info", "retained": True}, {"severity": "critical", "retained": True}])
    assert r["retention_pct"] == 100.0
    assert r["critical"] == 1
    assert r["healthy"]
