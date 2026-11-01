from app.services.app_marketplace_321k_milestone import celebrate_321k
def test_321k():
    assert "321,000" in celebrate_321k()["milestone"]
