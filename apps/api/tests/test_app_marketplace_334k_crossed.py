from app.services.app_marketplace_334k_crossed import celebrate_334k
def test_334k_crossed():
    assert "334,000" in celebrate_334k()["milestone"]
