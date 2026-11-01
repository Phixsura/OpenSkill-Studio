from app.services.app_marketplace_324k_crossed import celebrate_324k_crossed
def test_324kc():
    r = celebrate_324k_crossed()
    assert "324,000" in r["milestone"]
    assert r["session"]["milestones"] == 22
    assert "NEVER STOPS" in r["status"]
