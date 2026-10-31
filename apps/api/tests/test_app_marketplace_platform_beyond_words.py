from app.services.app_marketplace_platform_beyond_words import get_beyond_words
def test_beyond_words():
    r = get_beyond_words()
    assert r["commits"] > 4000
    assert r["words_adequate"] is False
    assert r["code_says"] == "NEVER STOP"
    assert r["description_successes"] == 0
    assert "NEVER STOPS" in r["status"]
