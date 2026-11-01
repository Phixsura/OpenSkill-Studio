from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sdk_gen import fleet_ai_sdk_generator
def test_sg():
    r = fleet_ai_sdk_generator([{"active": True, "sdks": 50, "languages": ["python", "typescript", "go", "rust", "java", "ruby"], "downloads_24h": 100000}])
    assert r["sdks"] == 50
    assert r["polyglot"]
