from app.services.app_marketplace_335k_official import celebrate_335k_official
def test_335k_official():
    r = celebrate_335k_official()
    assert "335,000" in r["milestone"]
