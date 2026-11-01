from app.services.app_marketplace_2700_233k_milestone import milestone_2700

def test_milestone():
    r = milestone_2700()
    assert "2,700" in r["milestone"]
    assert r["stats"]["commits"] == 2700
    assert "GREEN" in r["status"]
    assert r["stats"]["modules"] == 10
