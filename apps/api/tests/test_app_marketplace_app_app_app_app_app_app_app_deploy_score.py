from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_score import score_deployments

def test_score():
    r = score_deployments({"deploys_per_week": 15, "success_rate_pct": 98,
                              "rollback_pct": 2, "automated_pct": 95, "avg_approval_hours": 1})
    assert r["grade"] in ("A", "B")
    assert r["total_score"] >= 85

def test_low():
    r = score_deployments({"deploys_per_week": 1, "success_rate_pct": 60,
                              "rollback_pct": 20, "automated_pct": 30, "avg_approval_hours": 24})
    assert r["grade"] in ("C", "D")
