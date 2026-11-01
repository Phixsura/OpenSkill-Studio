from app.services.app_marketplace_324k_official import celebrate_324k_official
def test_324ko():
    r = celebrate_324k_official()
    assert "324,000" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
