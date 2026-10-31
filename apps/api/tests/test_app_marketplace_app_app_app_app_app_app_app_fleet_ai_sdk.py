from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sdk import fleet_ai_sdk
def test_sdk():
    r = fleet_ai_sdk([{"language": "Python", "downloads_30d": 500000, "active_users": 50000},
                      {"language": "TypeScript", "downloads_30d": 300000, "active_users": 30000}])
    assert r["languages"] == 2
    assert r["adopted"]
