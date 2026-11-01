from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_zero_trust_v9 import fleet_zero_trust_v9
def test_zt_v9():
    r = fleet_zero_trust_v9([{"enforced": True, "mfa_required": True, "active_sessions": 500}])
    assert r["enforced"] == 1
    assert r["healthy"]
