from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_growth_rate import fleet_growth_rate
def test_growth():
    r = fleet_growth_rate([{"value": 100}, {"value": 200}, {"value": 400}])
    assert r["avg_rate"] == 150.0
    assert r["accelerating"]
