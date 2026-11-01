from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_zig import fleet_zig_status
def test_zig():
    r = fleet_zig_status([{"running": True, "rps": 500000, "memory_kb": 512}])
    assert r["rps"] == 500000
    assert r["ultra_light"]
