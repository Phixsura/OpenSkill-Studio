from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_changelog import fleet_ai_changelog
def test_cl():
    r = fleet_ai_changelog([{"active": True, "releases": 100, "features": 500, "fixes": 300, "subscribers": 10000}])
    assert r["releases"] == 100
    assert r["informative"]
