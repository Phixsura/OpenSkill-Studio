from app.services.app_marketplace_305k_solid import celebrate_305k_solid
def test_305ks():
    assert "305,000" in celebrate_305k_solid()["milestone"]
