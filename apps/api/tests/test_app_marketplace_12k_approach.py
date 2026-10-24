from app.services.app_marketplace_12k_approach import celebrate_12k_approach
def test_m():
    assert "12,000" in celebrate_12k_approach()["milestone"]
