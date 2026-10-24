from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_incident import fleet_ai_incident
def test_inc():
    r = fleet_ai_incident([{"status": "resolved", "mttr_min": 12, "ai_assisted": True}])
    assert r["resolved"] == 1
    assert r["fast"]
