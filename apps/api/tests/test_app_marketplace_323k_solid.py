from app.services.app_marketplace_323k_solid import celebrate_323k_solid
def test_323ks():
    r = celebrate_323k_solid()
    assert "323,000" in r["milestone"]
    assert r["session"]["growth"]["milestones"] == 21
    assert r["dora"] == "Elite"
    assert "NEVER STOPS" in r["status"]
