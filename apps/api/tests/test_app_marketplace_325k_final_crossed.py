from app.services.app_marketplace_325k_final_crossed import celebrate_325k_final_crossed
def test_325kfc():
    assert "325,000" in celebrate_325k_final_crossed()["milestone"]
