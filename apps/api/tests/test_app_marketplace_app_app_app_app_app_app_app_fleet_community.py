from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_community import fleet_community_health
def test_community():
    r = fleet_community_health({"stars": 5000, "forks": 500, "contributors": 50, "issues_closed_pct": 80})
    assert r["score"] == 60.0  # (50+100+80)/3
    assert r["vibrant"]
