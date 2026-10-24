from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_translate import fleet_ai_translate
def test_ait():
    r = fleet_ai_translate([{"active": True, "translations_24h": 2000000, "languages": 100}])
    assert r["translations_24h"] == 2000000
    assert r["multilingual"]
