from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_valkey import fleet_valkey_status
def test_vk():
    r = fleet_valkey_status([{"online": True, "keys": 10000000, "memory_gb": 32}])
    assert r["keys"] == 10000000
    assert r["all_online"]
