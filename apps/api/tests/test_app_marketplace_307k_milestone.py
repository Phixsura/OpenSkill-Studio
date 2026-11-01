from app.services.app_marketplace_307k_milestone import celebrate_307k
def test_307k():
    assert "307,000" in celebrate_307k()["milestone"]
