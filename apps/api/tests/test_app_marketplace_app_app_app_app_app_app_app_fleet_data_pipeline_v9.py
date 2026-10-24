from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_pipeline_v9 import fleet_data_pipeline_v9
def test_dp_v9():
    r = fleet_data_pipeline_v9([{"status": "completed", "rows": 1000000}])
    assert r["rows_processed"] == 1000000
    assert r["healthy"]
