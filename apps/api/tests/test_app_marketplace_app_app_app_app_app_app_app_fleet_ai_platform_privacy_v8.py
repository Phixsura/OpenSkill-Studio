from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_privacy_v8 import fleet_ai_privacy_v8
def test_pv8():
    r = fleet_ai_privacy_v8([{"active": True, "pii_detected": 1000000, "redacted": 1000000, "gdpr": True, "ccpa": True}])
    assert r["private"]
