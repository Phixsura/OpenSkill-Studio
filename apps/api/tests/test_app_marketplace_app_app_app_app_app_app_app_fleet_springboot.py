from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_springboot import fleet_springboot_status
def test_sb():
    r = fleet_springboot_status([{"status": "UP", "beans": 500, "heap_pct": 60}])
    assert r["beans"] == 500
    assert r["all_up"]
