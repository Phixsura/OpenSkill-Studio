from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_drift_det import fleet_ai_drift_detection
def test_dd():
    r = fleet_ai_drift_detection([{"active": True, "alerts_24h": 2, "drift_score": 0.045, "retrained": 1}])
    assert r["drift_score"] == 0.045
    assert r["stable"]
