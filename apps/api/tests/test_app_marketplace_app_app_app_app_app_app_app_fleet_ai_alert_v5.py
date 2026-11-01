from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_alert_v5 import fleet_ai_alerting_v5
def test_av5():
    r = fleet_ai_alerting_v5([{"active": True, "alerts_24h": 500, "acked": 490, "auto_resolved": 400, "noise_reduction_pct": 75}])
    assert r["auto_resolved"] == 400
    assert r["smart"]
