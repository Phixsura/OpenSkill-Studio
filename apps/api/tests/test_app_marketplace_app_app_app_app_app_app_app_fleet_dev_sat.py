from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dev_sat import fleet_dev_satisfaction
def test_sat():
    r = fleet_dev_satisfaction([{"satisfaction": 5}, {"satisfaction": 4}, {"satisfaction": 3}])
    assert r["avg_score"] == 4.0
    assert r["happy_pct"] == 66.7
    assert r["good"]
