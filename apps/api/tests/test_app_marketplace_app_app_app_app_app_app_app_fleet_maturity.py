from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_maturity import fleet_maturity_score
def test_maturity():
    r = fleet_maturity_score({"observability": 90, "reliability": 85, "security": 80, "automation": 95, "governance": 70})
    assert r["score"] == 84.0
    assert r["level"] == "Advanced"
