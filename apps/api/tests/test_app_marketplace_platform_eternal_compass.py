from app.services.app_marketplace_platform_eternal_compass import get_eternal_compass
def test_eternal_compass():
    r = get_eternal_compass()
    assert r["readings"] > 4000
    assert "Quality" in r["true_north"]
    assert r["needle"].startswith("ROCK STEADY")
    assert len(r["environment"]) == 3
    assert "NEVER STOPS" in r["status"]
