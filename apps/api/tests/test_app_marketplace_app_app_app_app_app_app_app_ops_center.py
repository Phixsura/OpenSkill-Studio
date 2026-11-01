from app.services.app_marketplace_app_app_app_app_app_app_app_ops_center import build_ops_center

def test_green():
    r = build_ops_center({
        "services": {"healthy_pct": 100, "unhealthy": 0},
        "infrastructure": {"uptime_pct": 99.99},
        "security": {"compliance_pct": 100, "violations": 0},
        "deployments": {"success_rate": 98, "failed": 0},
    })
    assert r["status"] == "green"
    assert r["overall_score"] >= 95
    assert len(r["action_items"]) == 0

def test_yellow():
    r = build_ops_center({
        "services": {"healthy_pct": 80, "unhealthy": 3},
        "infrastructure": {"uptime_pct": 95},
        "security": {"compliance_pct": 90, "violations": 2},
        "deployments": {"success_rate": 85, "failed": 2},
    })
    assert r["status"] in ("yellow", "red")
    assert len(r["action_items"]) >= 2
