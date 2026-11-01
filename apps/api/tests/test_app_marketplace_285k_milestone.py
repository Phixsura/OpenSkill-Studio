from app.services.app_marketplace_285k_milestone import celebrate_285k
def test_285k():
    r = celebrate_285k()
    assert "285,000" in r["milestone"]
