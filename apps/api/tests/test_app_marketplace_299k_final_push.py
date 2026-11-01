from app.services.app_marketplace_299k_final_push import celebrate_299k_final_push
def test_m():
    assert "299,000" in celebrate_299k_final_push()["milestone"]
