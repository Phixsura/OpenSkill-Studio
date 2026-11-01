from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ttv import fleet_time_to_value
def test_ttv():
    r = fleet_time_to_value([{"ttv_hours": 2}, {"ttv_hours": 48}, {"ttv_hours": 12}])
    assert r["avg_ttv_hours"] == 20.7
    assert r["fast_activation"] == 2
    assert r["fast_pct"] == 66.7
