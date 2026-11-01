from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_quality_v7 import fleet_ai_quality_v7
def test_qv7():
    r = fleet_ai_quality_v7([{"active": True, "coverage": 95, "debt_h": 100, "bugs": 5, "smells": 20}])
    assert r["coverage"] == 95.0
    assert r["clean"]
