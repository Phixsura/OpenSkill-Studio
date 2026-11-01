from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_competitive_v7 import fleet_ai_competitive_v7
def test_cv7():
    r = fleet_ai_competitive_v7([{"active": True, "competitors": 30, "win_pct": 75, "share_pct": 40, "ahead": 50}])
    assert r["win_rate"] == 75.0
    assert r["leading"]
