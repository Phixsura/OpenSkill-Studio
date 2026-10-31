from app.services.app_marketplace_325k_approaching import celebrate_325k_approaching
def test_325k():
    assert "325,000" in celebrate_325k_approaching()["target"]
