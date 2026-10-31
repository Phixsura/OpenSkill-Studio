from app.services.app_marketplace_16k_320k_double import celebrate_double_approaching
def test_double():
    r = celebrate_double_approaching()
    assert "16,000" in r["targets"][0]
    assert "320,000" in r["targets"][1]
