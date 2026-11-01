from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kv import fleet_kv_store
def test_kv():
    r = fleet_kv_store([{"keys": 1000000, "reads_24h": 50000000, "writes_24h": 1000000}])
    assert r["keys"] == 1000000
    assert r["active"]
