from app.services.app_marketplace_328k_milestone import celebrate_328k
def test_328k():
    r = celebrate_328k()
    assert "328,000" in r["milestone"]
