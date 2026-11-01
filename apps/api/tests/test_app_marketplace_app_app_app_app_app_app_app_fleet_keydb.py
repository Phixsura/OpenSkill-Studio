from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_keydb import fleet_keydb_status
def test_kdb():
    r = fleet_keydb_status([{"online": True, "keys": 5000000, "ops_per_sec": 500000}])
    assert r["keys"] == 5000000
    assert r["all_online"]
