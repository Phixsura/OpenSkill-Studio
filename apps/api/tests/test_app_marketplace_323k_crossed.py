from app.services.app_marketplace_323k_crossed import celebrate_323k_crossed
def test_323kc():
    assert "323,000" in celebrate_323k_crossed()["milestone"]
    assert celebrate_323k_crossed()["session"]["milestones"] == 21
