from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_watermark import fleet_ai_watermark
def test_wm():
    r = fleet_ai_watermark([{"active": True, "watermarked_24h": 1000000, "verified_24h": 500000}])
    assert r["watermarked_24h"] == 1000000
    assert r["all_active"]
