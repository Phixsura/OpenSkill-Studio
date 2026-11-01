from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_map_v9 import fleet_service_map_v9
def test_smap_v9():
    r = fleet_service_map_v9([{"mapped": True, "connections": 5, "on_critical_path": True}])
    assert r["mapped"] == 1
    assert r["healthy"]
