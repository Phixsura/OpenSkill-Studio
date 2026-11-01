from app.services.app_marketplace_302k import celebrate_302k
def test_m():
    assert "302,000" in celebrate_302k()["milestone"]
