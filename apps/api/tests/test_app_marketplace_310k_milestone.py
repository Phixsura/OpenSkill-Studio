from app.services.app_marketplace_310k_milestone import celebrate_310k
def test_310k():
    assert "310,000" in celebrate_310k()["milestone"]
