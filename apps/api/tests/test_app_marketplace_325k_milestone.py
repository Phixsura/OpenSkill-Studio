from app.services.app_marketplace_325k_milestone import celebrate_325k
def test_325k():
    r = celebrate_325k()
    assert "325,000" in r["milestone"]
    assert r["session"]["milestones"] == 23
    assert "NEVER STOPS" in r["status"]
