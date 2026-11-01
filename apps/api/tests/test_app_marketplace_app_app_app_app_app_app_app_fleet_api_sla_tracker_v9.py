from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_sla_tracker_v9 import fleet_api_sla_tracker_v9
def test_ast2_v9():
    r = fleet_api_sla_tracker_v9([{"met": True, "breached": False, "credits_owed": 0}])
    assert r["met"] == 1
    assert r["healthy"]
