from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dev_sdk import fleet_ai_dev_sdk
def test_sdk():
    r = fleet_ai_dev_sdk([{"active": True, "languages": ["python", "typescript", "go", "rust"], "downloads_24h": 50000, "developers": 20000}])
    assert r["languages"] == 4
    assert r["adopted"]
