from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_auth0 import fleet_auth0_status
def test_a0():
    r = fleet_auth0_status([{"active": True, "logins_24h": 1000000, "mfa_pct": 85}])
    assert r["logins_24h"] == 1000000
    assert r["secure"]
