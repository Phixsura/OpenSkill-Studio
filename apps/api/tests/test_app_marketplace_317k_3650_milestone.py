from app.services.app_marketplace_317k_3650_milestone import celebrate_317k_3650
def test_317k3650():
    assert "317,000" in celebrate_317k_3650()["milestones"][0]
    assert "3,650" in celebrate_317k_3650()["milestones"][1]
