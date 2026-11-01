from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_watermark import fleet_ai_watermark
def test_wm():
    r = fleet_ai_watermark([{"active": True, "watermarked_24h": 1000000, "detected_24h": 950000}])
    assert r["detection_rate"] == 95.0
