from app.services.app_marketplace_324k_milestone import celebrate_324k
def test_324k():
    assert "324,000" in celebrate_324k()["milestone"]
