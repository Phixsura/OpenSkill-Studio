from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_lead_time_v9 import fleet_lead_time_v9
def test_lt2_v9():
    r = fleet_lead_time_v9([{"lead_time_min": 15}, {"lead_time_min": 20}])
    assert r["avg_lead_time_min"] == 17.5
    assert r["dora_class"] == "Elite"
    assert r["healthy"]
