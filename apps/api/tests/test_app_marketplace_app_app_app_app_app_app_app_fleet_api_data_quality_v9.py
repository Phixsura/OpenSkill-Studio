from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_data_quality_v9 import fleet_api_data_quality_v9
def test_adq2_v9():
    r = fleet_api_data_quality_v9([{"data_quality_score": 99, "anomalies": 0}])
    assert r["avg_score"] == 99.0
    assert r["healthy"]
