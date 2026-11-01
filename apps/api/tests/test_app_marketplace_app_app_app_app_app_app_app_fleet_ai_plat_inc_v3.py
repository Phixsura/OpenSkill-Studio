from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_inc_v3 import fleet_ai_incident_v3
def test_iv3():
    r = fleet_ai_incident_v3([{"active": True, "incidents_30d": 10, "p1": 2, "mttr_min": 12, "postmortems": 2}])
    assert r["mttr_min"] == 12.0
    assert r["learning"]
