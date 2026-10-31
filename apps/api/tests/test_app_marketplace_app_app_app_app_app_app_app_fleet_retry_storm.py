from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_retry_storm import fleet_retry_storm
def test_storm():
    r = fleet_retry_storm([{"retry_ratio": 1}, {"retry_ratio": 5}, {"retry_ratio": 4}, {"retry_ratio": 6}])
    assert r["amplifying"] == 3
    assert r["storm"]
