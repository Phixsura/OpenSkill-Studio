from app.services.app_marketplace_325k_crossed import celebrate_325k_crossed
def test_325kc():
    r = celebrate_325k_crossed()
    assert "325,000" in r["milestone"]
    assert r["session"]["growth"]["milestones"] == 23
    assert "NEVER STOPS" in r["status"]
