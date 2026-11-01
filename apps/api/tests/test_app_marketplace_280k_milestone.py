from app.services.app_marketplace_280k_milestone import celebrate_280k
def test_280k():
    r = celebrate_280k()
    assert "280,000" in r["milestone"]
    assert r["files"] == 10158
