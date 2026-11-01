from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_resp_ai import fleet_ai_responsible
def test_rai():
    r = fleet_ai_responsible([{"active": True, "assessments": 500, "principles": 20, "compliance_pct": 98}])
    assert r["assessments"] == 500
    assert r["responsible"]
