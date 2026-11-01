from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_lead_time import fleet_lead_time
def test_lead():
    r = fleet_lead_time([{"lead_time_min": 30}, {"lead_time_min": 45}, {"lead_time_min": 90}])
    assert r["avg_lead_time_min"] == 55.0
    assert r["under_hour"] == 2
    assert r["elite"]
