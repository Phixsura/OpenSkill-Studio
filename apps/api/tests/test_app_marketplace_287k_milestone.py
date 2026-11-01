from app.services.app_marketplace_287k_milestone import celebrate_287k
def test_287k():
    assert "287,000" in celebrate_287k()["milestone"]
