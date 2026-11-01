from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_anomaly import fleet_ai_anomaly
def test_ad():
    r = fleet_ai_anomaly([{"active": True, "metrics": 10000, "anomalies_24h": 15, "fp_rate": 2.1}])
    assert r["metrics"] == 10000
    assert r["precise"]
