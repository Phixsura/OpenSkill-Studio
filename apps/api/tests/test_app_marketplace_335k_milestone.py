from app.services.app_marketplace_335k_milestone import celebrate_335k
def test_335k():
    assert "335,000" in celebrate_335k()["milestone"]
