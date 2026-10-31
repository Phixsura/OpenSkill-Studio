from app.services.app_marketplace_284k_milestone import celebrate_284k
def test_284k():
    r = celebrate_284k()
    assert "284,000" in r["milestone"]
