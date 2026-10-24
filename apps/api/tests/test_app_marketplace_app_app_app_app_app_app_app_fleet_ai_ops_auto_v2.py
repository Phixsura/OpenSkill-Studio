from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ops_auto_v2 import fleet_ai_ops_automation_v2
def test_oav2():
    r = fleet_ai_ops_automation_v2([{"active": True, "automations": 500, "tasks_24h": 100000, "manual": 5}])
    assert r["automations"] == 500
    assert r["autonomous"]
