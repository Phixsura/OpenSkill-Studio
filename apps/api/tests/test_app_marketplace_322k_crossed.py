from app.services.app_marketplace_322k_crossed import celebrate_322k_crossed
def test_322kc():
    r = celebrate_322k_crossed()
    assert "322,000" in r["milestone"]
    assert r["session"]["milestones"] == 20
