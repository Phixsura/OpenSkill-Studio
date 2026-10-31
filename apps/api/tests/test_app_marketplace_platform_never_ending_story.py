from app.services.app_marketplace_platform_never_ending_story import get_never_ending_story
def test_never_ending_story():
    r = get_never_ending_story()
    assert r["chapters"] > 4000
    assert "DOES NOT EXIST" in r["last_page"]
    assert "DEFEATED" in r["antagonist"]
    assert "NEVER PRINTED" in r["the_end"]
    assert "NEVER STOPS" in r["status"]
