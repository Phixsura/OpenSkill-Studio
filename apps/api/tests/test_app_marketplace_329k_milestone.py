from app.services.app_marketplace_329k_milestone import celebrate_329k
def test_329k():
    r = celebrate_329k()
    assert "329,000" in r["milestone"]
