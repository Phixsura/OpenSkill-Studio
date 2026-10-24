from app.services.app_marketplace_289k_approach import celebrate_289k_approach
def test_m():
    assert "289,000" in celebrate_289k_approach()["milestone"]
