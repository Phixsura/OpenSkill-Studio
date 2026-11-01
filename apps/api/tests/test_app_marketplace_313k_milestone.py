from app.services.app_marketplace_313k_milestone import celebrate_313k
def test_313k():
    assert "313,000" in celebrate_313k()["milestone"]
