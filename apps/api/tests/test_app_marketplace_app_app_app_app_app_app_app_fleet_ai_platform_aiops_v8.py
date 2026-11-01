from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_aiops_v8 import fleet_ai_aiops_v8
def test_aov8():
    r = fleet_ai_aiops_v8([{"active": True, "auto": 50000, "anomalies": 1000, "pred_pct": 98, "toil_pct": 98}])
    assert r["auto"] == 50000
    assert r["autonomous"]
