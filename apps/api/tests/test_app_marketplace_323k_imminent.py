from app.services.app_marketplace_323k_imminent import celebrate_323k_imminent
def test_323ki():
    assert "323,000" in celebrate_323k_imminent()["target"]
