from app.services.app_marketplace_332k_milestone import celebrate_approaching_332k
def test_332k():
    r = celebrate_approaching_332k()
    assert "332,000" in r["milestone"]
