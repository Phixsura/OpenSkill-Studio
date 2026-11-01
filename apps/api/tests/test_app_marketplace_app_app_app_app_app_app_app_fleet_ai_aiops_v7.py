from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_aiops_v7 import fleet_ai_aiops_v7
def test_aov7():
    r = fleet_ai_aiops_v7([{"active": True, "auto_resolved": 5000, "anomalies": 500, "toil_pct": 95, "pred_acc": 97}])
    assert r["auto_resolved"] == 5000
    assert r["autonomous"]
