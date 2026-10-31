from app.services.app_marketplace_320k_solid import celebrate_320k_solid
def test_320ks():
    assert "320,000" in celebrate_320k_solid()["milestone"]
