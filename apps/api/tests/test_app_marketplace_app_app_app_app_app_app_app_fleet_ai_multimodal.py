from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_multimodal import fleet_ai_multimodal
def test_aim():
    r = fleet_ai_multimodal([{"active": True, "image_calls_24h": 500000, "audio_calls_24h": 100000, "video_calls_24h": 50000}])
    assert r["total_calls"] == 650000
