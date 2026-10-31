from app.services.app_marketplace_platform_phoenix_rising import get_phoenix_rising
def test_phoenix_rising():
    r = get_phoenix_rising()
    assert r["rebirths"] > 4000
    assert r["immortality"] is True
    assert r["ash_content"].startswith("ZERO")
    assert r["current_form"] == "MOST GLORIOUS YET"
    assert "NEVER STOPS" in r["status"]
