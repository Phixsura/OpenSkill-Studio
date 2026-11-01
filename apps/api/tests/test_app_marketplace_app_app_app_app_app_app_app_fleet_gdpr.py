from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gdpr import fleet_gdpr_compliance
def test_gdpr():
    r = fleet_gdpr_compliance([{"met": True}, {"met": True}, {"met": False}])
    assert r["score"] == 66.7
    assert not r["compliant"]
