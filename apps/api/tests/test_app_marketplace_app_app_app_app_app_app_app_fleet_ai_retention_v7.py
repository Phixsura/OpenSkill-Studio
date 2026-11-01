from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_retention_v7 import fleet_ai_retention_v7
def test_rv7():
    r = fleet_ai_retention_v7([{"active": True, "d1_pct": 80, "d7_pct": 65, "d30_pct": 55, "d90_pct": 45}])
    assert r["d30"] == 55.0
    assert r["sticky"]
