from app.services.app_marketplace_305k_milestone import celebrate_305k
def test_305k():
    assert "305,000" in celebrate_305k()["milestone"]
