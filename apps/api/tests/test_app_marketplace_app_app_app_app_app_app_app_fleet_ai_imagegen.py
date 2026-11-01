from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_imagegen import fleet_ai_imagegen
def test_ig():
    r = fleet_ai_imagegen([{"active": True, "images_24h": 500000, "avg_gen_sec": 10}])
    assert r["images_24h"] == 500000
    assert r["fast"]
