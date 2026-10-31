from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_talent_v7 import fleet_ai_talent_v7
def test_tv7():
    r = fleet_ai_talent_v7([{"active": True, "engineers": 500, "hiring": 50, "retention_pct": 95}])
    assert r["engineers"] == 500
    assert r["strong"]
