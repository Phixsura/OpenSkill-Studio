from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_unleash import fleet_unleash_status
def test_unleash():
    r = fleet_unleash_status([{"enabled": True, "impressions_24h": 50000}, {"enabled": False, "stale": True}])
    assert r["enabled"] == 1
    assert r["stale"] == 1
    assert r["healthy"]
