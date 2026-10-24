from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_consumer_lag import fleet_consumer_lag
def test_lag():
    r = fleet_consumer_lag([{"lag": 500}, {"lag": 15000}])
    assert r["total_lag"] == 15500
    assert r["behind"] == 1
    assert not r["caught_up"]
