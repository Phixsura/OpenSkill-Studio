from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_img_gen import fleet_ai_image_generation
def test_ig():
    r = fleet_ai_image_generation([{"active": True, "images_24h": 2000000, "latency_s": 3.5, "resolutions": ["512x512", "1024x1024"]}])
    assert r["images_24h"] == 2000000
    assert r["fast"]
