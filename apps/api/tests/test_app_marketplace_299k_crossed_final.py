from app.services.app_marketplace_299k_crossed_final import celebrate_299k_final_crossed
def test_m():
    assert "299,000" in celebrate_299k_final_crossed()["milestone"]
