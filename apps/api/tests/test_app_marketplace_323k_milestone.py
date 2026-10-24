from app.services.app_marketplace_323k_milestone import celebrate_323k
def test_323k():
    assert "323,000" in celebrate_323k()["milestone"]
