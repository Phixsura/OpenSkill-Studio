from app.services.app_marketplace_314k_milestone import celebrate_314k
def test_314k():
    assert "314,000" in celebrate_314k()["milestone"]
