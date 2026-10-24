from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_privacy_v7 import fleet_ai_privacy_v7
def test_pv7():
    r = fleet_ai_privacy_v7([{"active": True, "pii": 50000, "redacted": 50000, "gdpr": True}])
    assert r["private"]
