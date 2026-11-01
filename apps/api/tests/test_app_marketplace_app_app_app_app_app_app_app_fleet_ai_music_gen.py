from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_music_gen import fleet_ai_music_gen
def test_mg():
    r = fleet_ai_music_gen([{"active": True, "tracks_24h": 100000, "genres": ["pop", "rock", "jazz", "classical", "electronic", "ambient"], "avg_duration_s": 180}])
    assert r["tracks_24h"] == 100000
    assert r["creative"]
