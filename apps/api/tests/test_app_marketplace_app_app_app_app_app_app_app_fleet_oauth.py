from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_oauth import fleet_oauth_stats
def test_oauth():
    r = fleet_oauth_stats({"issued": 1000, "revoked": 50, "expired": 200})
    assert r["active"] == 750
    assert r["revocation_rate"] == 5.0
