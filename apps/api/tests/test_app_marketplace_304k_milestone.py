from app.services.app_marketplace_304k_milestone import celebrate_304k
def test_304k():
    assert "304,000" in celebrate_304k()["milestone"]
