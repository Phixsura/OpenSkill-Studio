from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ocr import fleet_ai_ocr
def test_ocr():
    r = fleet_ai_ocr([{"active": True, "pages_24h": 1000000, "accuracy_pct": 99}])
    assert r["pages_24h"] == 1000000
    assert r["all_active"]
