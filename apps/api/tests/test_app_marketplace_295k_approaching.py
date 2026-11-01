from app.services.app_marketplace_295k_approaching import celebrate_295k_approaching
def test_m():
    assert "295,000" in celebrate_295k_approaching()["milestone"]
