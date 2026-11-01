from app.services.app_marketplace_289k_milestone import celebrate_289k
def test_289k():
    assert "289,000" in celebrate_289k()["milestone"]
