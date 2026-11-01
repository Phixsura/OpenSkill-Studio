from app.services.app_marketplace_334k_milestone import celebrate_334k
def test_334k():
    assert "334,000" in celebrate_334k()["milestone"]
