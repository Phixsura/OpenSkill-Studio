from app.services.app_marketplace_309k_milestone import celebrate_309k
def test_309k():
    assert "309,000" in celebrate_309k()["milestone"]
