from app.services.app_marketplace_304k_solid import celebrate_304k_solid
def test_304ks():
    assert "304,600" in celebrate_304k_solid()["milestone"]
