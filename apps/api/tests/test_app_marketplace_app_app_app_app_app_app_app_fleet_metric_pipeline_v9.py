from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_metric_pipeline_v9 import fleet_metric_pipeline_v9
def test_mp2_v9():
    r = fleet_metric_pipeline_v9([{"active": True, "metrics_per_sec": 50000, "cardinality": 100000}])
    assert r["metrics_per_sec"] == 50000
    assert r["healthy"]
