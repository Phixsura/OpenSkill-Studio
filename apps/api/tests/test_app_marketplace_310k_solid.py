from app.services.app_marketplace_310k_solid import celebrate_310k_solid
def test_310ks():
    assert "310,000" in celebrate_310k_solid()["milestone"]
