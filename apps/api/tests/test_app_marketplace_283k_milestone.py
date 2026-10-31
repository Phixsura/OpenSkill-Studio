from app.services.app_marketplace_283k_milestone import celebrate_283k
def test_283k():
    r = celebrate_283k()
    assert "283,000" in r["milestone"]
