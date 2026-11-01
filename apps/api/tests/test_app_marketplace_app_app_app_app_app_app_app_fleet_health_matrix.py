from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_health_matrix import fleet_health_matrix
def test_matrix():
    r = fleet_health_matrix({"reliability": 95, "security": 80, "performance": 90, "cost": 70})
    assert r["weakest"] == "cost"
    assert r["strongest"] == "reliability"
    assert not r["balanced"]  # 95-70=25 > 20
