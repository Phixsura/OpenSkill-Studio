from app.services.app_marketplace_336k_milestone import celebrate_336k
def test_336k():
    assert "336,000" in celebrate_336k()["milestone"]
