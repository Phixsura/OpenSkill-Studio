from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_text_ext import fleet_ai_text_extractor
def test_te():
    r = fleet_ai_text_extractor([{"active": True, "extracted_24h": 5000000, "types": ["pdf", "image", "video", "audio"], "accuracy": 97}])
    assert r["types"] == 4
    assert r["versatile"]
