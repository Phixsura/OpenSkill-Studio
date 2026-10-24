from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_speech import fleet_ai_speech
def test_sp():
    r = fleet_ai_speech([{"active": True, "hours_24h": 10000, "languages": ["en", "zh", "es", "fr"], "wer": 3.2}])
    assert r["languages"] == 4
    assert r["accurate"]
