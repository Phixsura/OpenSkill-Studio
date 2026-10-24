from app.services.app_marketplace_291k_12k_approach import celebrate_291k_12k
def test_m():
    assert "291,000" in celebrate_291k_12k()["milestone"]
