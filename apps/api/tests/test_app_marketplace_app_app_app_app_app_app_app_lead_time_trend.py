from app.services.app_marketplace_app_app_app_app_app_app_app_lead_time_trend import lead_time_trend
def test_improving():
    r = lead_time_trend([{"lead_time_hours": 48}, {"lead_time_hours": 36}, {"lead_time_hours": 4}, {"lead_time_hours": 2}])
    assert r["trend"] == "improving"
