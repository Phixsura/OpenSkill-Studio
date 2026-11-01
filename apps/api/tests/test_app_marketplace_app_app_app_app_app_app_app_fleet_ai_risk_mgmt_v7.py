from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_risk_mgmt_v7 import fleet_ai_risk_mgmt_v7
def test_rmv7():
    r = fleet_ai_risk_mgmt_v7([{"active": True, "risks": 100, "mitigated": 100, "score": 95}])
    assert r["managed"]
