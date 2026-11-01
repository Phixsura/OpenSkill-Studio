from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_eda import fleet_eda_health
def test_eda():
    r = fleet_eda_health([{"consumer_lag": 100, "events_per_sec": 500}, {"consumer_lag": 5000, "events_per_sec": 200}])
    assert r["healthy"] == 1
    assert r["total_eps"] == 700
    assert not r["all_healthy"]
