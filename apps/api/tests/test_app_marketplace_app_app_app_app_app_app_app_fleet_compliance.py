from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_compliance import fleet_compliance_score
def test_compliance():
    r = fleet_compliance_score([{"status": "pass"}, {"status": "pass"}, {"status": "fail"}])
    assert r["score"] == 66.7
    assert r["grade"] == "F"
