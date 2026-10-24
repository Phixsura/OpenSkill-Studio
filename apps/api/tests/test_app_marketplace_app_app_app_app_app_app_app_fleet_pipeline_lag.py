from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pipeline_lag import fleet_pipeline_lag
def test_lag():
    r = fleet_pipeline_lag([{"lag_minutes": 5}, {"lag_minutes": 30}])
    assert r["lagging"] == 1
    assert r["max_lag_min"] == 30
    assert not r["fresh"]
