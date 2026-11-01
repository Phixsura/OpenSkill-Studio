from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_log_vol import fleet_log_volume
def test_log_vol():
    r = fleet_log_volume([{"gb_per_day": 100}, {"gb_per_day": 150}])
    assert r["total_gb_per_day"] == 250
    assert r["daily_cost"] == 125.0
    assert r["expensive"]
