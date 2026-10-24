from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_multimodal import fleet_ai_multimodal
def test_mm():
    r = fleet_ai_multimodal([{"active": True, "modalities": ["text", "image", "audio"], "requests_24h": 1000000}])
    assert r["multimodal"]
    assert "image" in r["modalities"]
