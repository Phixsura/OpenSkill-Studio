from app.services.app_marketplace_295k_milestone import celebrate_295k
def test_295k():
    assert "295,000" in celebrate_295k()["milestone"]
