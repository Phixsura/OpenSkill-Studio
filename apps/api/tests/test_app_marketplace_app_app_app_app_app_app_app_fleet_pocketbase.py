from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pocketbase import fleet_pocketbase_status
def test_pb():
    r = fleet_pocketbase_status([{"running": True, "collections": 20, "records": 100000}])
    assert r["collections"] == 20
    assert r["all_running"]
