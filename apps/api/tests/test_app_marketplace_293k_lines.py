from app.services.app_marketplace_293k_lines import celebrate_293k
def test_m():
    assert "293,000" in celebrate_293k()["milestone"]
