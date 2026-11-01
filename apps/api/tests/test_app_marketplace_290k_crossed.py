from app.services.app_marketplace_290k_crossed import celebrate_290k_crossed
def test_290k():
    assert "290,000" in celebrate_290k_crossed()["milestone"]
    assert celebrate_290k_crossed()["dora"] == "Elite"
