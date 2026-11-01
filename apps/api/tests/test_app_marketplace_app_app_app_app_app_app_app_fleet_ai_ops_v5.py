from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ops_v5 import fleet_ai_ops_v5
def test_ov5():
    r = fleet_ai_ops_v5([{"active": True, "automations": 1000, "tasks": 500000, "toil_pct": 90}])
    assert r["automations"] == 1000
    assert r["autonomous"]
