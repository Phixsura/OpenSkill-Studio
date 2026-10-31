from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_sdk_v7 import fleet_ai_sdk_v7
def test_sv7():
    r = fleet_ai_sdk_v7([{"active": True, "languages": ["python", "typescript", "go", "rust", "java", "ruby", "csharp"], "downloads_30d": 5000000, "stars": 50000}])
    assert r["languages"] == 7
    assert r["popular"]
