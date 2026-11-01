from app.services.app_marketplace_under_1k_to_300k import celebrate_under_1k
def test_m():
    assert "1,000" in celebrate_under_1k()["milestone"]
    assert celebrate_under_1k()["remaining"] == 900
