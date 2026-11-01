from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_directus import fleet_directus_status
def test_dr():
    r = fleet_directus_status([{"running": True, "collections": 40, "items": 200000}])
    assert r["collections"] == 40
    assert r["all_running"]
