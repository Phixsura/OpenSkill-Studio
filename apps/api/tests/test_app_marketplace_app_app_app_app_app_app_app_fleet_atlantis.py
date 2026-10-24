from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_atlantis import fleet_atlantis_status
def test_atl():
    r = fleet_atlantis_status([{"atlantis_enabled": True, "plans_24h": 10, "applies_24h": 5}])
    assert r["plans_24h"] == 10
    assert r["active"]
