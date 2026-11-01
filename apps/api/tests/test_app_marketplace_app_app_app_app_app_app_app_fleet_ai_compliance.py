from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_compliance import fleet_ai_compliance
def test_comp():
    r = fleet_ai_compliance([{"status": "passed", "frameworks": ["SOC2", "GDPR", "HIPAA"]}])
    assert r["compliant"]
    assert "GDPR" in r["frameworks"]
