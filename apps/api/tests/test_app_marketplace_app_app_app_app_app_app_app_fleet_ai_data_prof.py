from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_prof import fleet_ai_data_profiler
def test_dp():
    r = fleet_ai_data_profiler([{"active": True, "datasets": 500, "columns": 5000, "anomalies": 50}])
    assert r["datasets"] == 500
    assert r["thorough"]
