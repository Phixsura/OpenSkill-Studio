from app.services.app_marketplace_299k_solid import celebrate_299k_solid
def test_m():
    assert "299,000" in celebrate_299k_solid()["milestone"]
