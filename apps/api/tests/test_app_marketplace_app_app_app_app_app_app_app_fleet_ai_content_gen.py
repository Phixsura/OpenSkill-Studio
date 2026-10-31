from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_content_gen import fleet_ai_content_gen
def test_cg():
    r = fleet_ai_content_gen([{"active": True, "content_24h": 500000, "words": 50000000, "quality": 92}])
    assert r["content_24h"] == 500000
    assert r["creative"]
