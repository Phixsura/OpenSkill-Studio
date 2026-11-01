from app.services.app_marketplace_16k_official import celebrate_16k_official
def test_16ko():
    assert "16,000" in celebrate_16k_official()["milestone"]
