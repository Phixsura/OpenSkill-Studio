from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gitops_mat import fleet_gitops_maturity
def test_gm():
    r = fleet_gitops_maturity({"declarative_pct": 90, "automated_sync_pct": 85, "immutable_infra_pct": 80})
    assert r["score"] == 85.0
    assert r["level"] == "Level 3"
