from app.services.app_marketplace_323k_final_crossed import celebrate_323k_final
def test_323kf():
    r = celebrate_323k_final()
    assert "323,000" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
