from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_telemetry import fleet_ai_telemetry
def test_tel():
    r = fleet_ai_telemetry([{"active": True, "metrics_24h": 100000000, "traces_24h": 50000000, "logs_24h": 500000000}])
    assert r["metrics_24h"] == 100000000
    assert r["observable"]
