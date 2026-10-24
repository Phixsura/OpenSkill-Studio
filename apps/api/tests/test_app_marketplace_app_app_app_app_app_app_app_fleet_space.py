from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_space import fleet_space_metrics
def test_space():
    r = fleet_space_metrics({"satisfaction": 80, "performance": 90, "activity": 70, "communication": 50, "efficiency": 85})
    assert r["score"] == 75.0
    assert "communication" in r["weak_dimensions"]
    assert not r["balanced"]
