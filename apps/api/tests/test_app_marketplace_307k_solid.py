from app.services.app_marketplace_307k_solid import celebrate_307k_solid
def test_307ks():
    assert "307,000" in celebrate_307k_solid()["milestone"]
