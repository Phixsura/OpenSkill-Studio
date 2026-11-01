from app.services.app_marketplace_291k_milestone import celebrate_291k
def test_291k():
    assert "291,000" in celebrate_291k()["milestone"]
