from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_catalog_v9 import fleet_service_catalog_v9
def test_sc_v9():
    r = fleet_service_catalog_v9([{"status": "active", "team": "platform", "tier": 1}, {"status": "active", "team": "data", "tier": 2}])
    assert r["teams"] == 2
    assert r["tier1_critical"] == 1
    assert r["healthy"]
