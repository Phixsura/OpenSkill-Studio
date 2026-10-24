from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_sla_v2 import fleet_ai_model_sla_v2
def test_msv2():
    r = fleet_ai_model_sla_v2([{"active": True, "models": 200, "met": 200, "breached": 0}])
    assert r["met"] == 200
    assert r["compliant"]
