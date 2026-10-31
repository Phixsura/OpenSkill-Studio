from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_inc_cmd_v2 import fleet_ai_incident_commander_v2
def test_icv2():
    r = fleet_ai_incident_commander_v2([{"active": True, "incidents": 200, "mttr_min": 8, "auto_remediated": 180}])
    assert r["incidents"] == 200
    assert r["fast"]
