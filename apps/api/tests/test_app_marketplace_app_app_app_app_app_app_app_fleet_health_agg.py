from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_health_agg import fleet_health_aggregator
def test_agg():
    r = fleet_health_aggregator([{"score": 90, "weight": 3}, {"score": 70, "weight": 2}, {"score": 40, "weight": 1}])
    assert r["overall_score"] == 75.0  # (270+140+40)/6
    assert r["critical"] == 1
    assert r["status"] == "degraded"
