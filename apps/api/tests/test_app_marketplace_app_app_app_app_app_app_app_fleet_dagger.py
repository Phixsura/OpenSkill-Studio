from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dagger import fleet_dagger_status
def test_dagger():
    r = fleet_dagger_status([{"cache_hits": 50, "operations": 200, "duration_sec": 120}])
    assert r["cache_hits"] == 50
    assert r["fast"]
