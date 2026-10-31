from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_translate import fleet_ai_translation
def test_tr():
    r = fleet_ai_translation([{"active": True, "translations_24h": 2000000, "lang_pairs": 100, "bleu": 55}])
    assert r["lang_pairs"] == 100
    assert r["fluent"]
