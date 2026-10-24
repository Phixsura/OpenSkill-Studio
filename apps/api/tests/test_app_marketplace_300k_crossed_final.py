from app.services.app_marketplace_300k_crossed_final import celebrate_300k_crossed_final
def test_300k():
    r = celebrate_300k_crossed_final()
    assert "300,000" in r["milestone"]
    assert r["lines"] == 300000
    assert r["dora"] == "Elite"
