from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_session_store_v9 import fleet_session_store_v9
def test_ss_v9():
    r = fleet_session_store_v9([{"active": True, "expired": False, "ttl_min": 30}])
    assert r["active"] == 1
    assert r["healthy"]
