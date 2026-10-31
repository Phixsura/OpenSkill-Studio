from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_trust_v7 import fleet_ai_platform_trust_v7
def test_ptv7():
    r = fleet_ai_platform_trust_v7([{"active": True, "score": 98, "transparency": 95, "certs": ["SOC2", "ISO27001"]}])
    assert r["score"] == 98.0
    assert r["trusted"]
