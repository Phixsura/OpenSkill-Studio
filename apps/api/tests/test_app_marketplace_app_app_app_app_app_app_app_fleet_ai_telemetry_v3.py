from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_telemetry_v3 import fleet_ai_telemetry_v3
def test_tv3():
    r = fleet_ai_telemetry_v3([{"active": True, "metrics_24h": 1000000000, "traces_24h": 500000000, "logs_24h": 5000000000, "storage_gb": 50000}])
    assert r["metrics"] == 1000000000
    assert r["comprehensive"]
