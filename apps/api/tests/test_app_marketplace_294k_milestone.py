from app.services.app_marketplace_294k_milestone import celebrate_294k
def test_294k():
    assert "294,000" in celebrate_294k()["milestone"]
