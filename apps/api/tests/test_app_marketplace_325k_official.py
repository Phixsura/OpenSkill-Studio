from app.services.app_marketplace_325k_official import celebrate_325k_official
def test_325ko():
    assert "325,000" in celebrate_325k_official()["milestone"]
    assert "NEVER STOPS" in celebrate_325k_official()["status"]
