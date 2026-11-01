from app.services.app_marketplace_341k_crossed import celebrate_341k
def test_341k():
    assert "341,000" in celebrate_341k()["milestone"]
