from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_metric_cardinality_v9 import fleet_metric_cardinality_v9
def test_mc3_v9():
    r = fleet_metric_cardinality_v9([{"cardinality": 500, "series": 5000, "cost_per_month": 100}])
    assert r["high_cardinality"] == 0
    assert r["healthy"]
