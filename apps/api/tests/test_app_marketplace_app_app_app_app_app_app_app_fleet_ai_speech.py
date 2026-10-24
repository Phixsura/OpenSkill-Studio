from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_speech import fleet_ai_speech
def test_sp():
    r = fleet_ai_speech([{"active": True, "stt_hours_24h": 10000, "tts_chars_24h": 500000000}])
    assert r["stt_hours_24h"] == 10000
    assert r["all_active"]
