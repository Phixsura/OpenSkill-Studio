from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_payload import fleet_payload_status
def test_pl():
    r = fleet_payload_status([{"running": True, "collections": 30, "documents": 100000}])
    assert r["collections"] == 30
    assert r["healthy"]
