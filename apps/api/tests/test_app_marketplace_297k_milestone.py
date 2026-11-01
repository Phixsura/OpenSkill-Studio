from app.services.app_marketplace_297k_milestone import celebrate_297k
def test_m():
    assert "297,000" in celebrate_297k()["milestone"]
