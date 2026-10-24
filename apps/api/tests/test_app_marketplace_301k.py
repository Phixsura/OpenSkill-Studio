from app.services.app_marketplace_301k import celebrate_301k
def test_m():
    assert "301,000" in celebrate_301k()["milestone"]
