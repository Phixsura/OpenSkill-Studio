from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_anomaly import fleet_ai_anomaly
def test_ano():
    r = fleet_ai_anomaly([{"active": True, "anomalies_24h": 500, "data_points_24h": 100000000}])
    assert r["anomalies_24h"] == 500
    assert r["all_active"]
