from app.services.app_marketplace_app_app_app_app_app_app_app_command_center import build_command_center

def test_green():
    r = build_command_center({
        "services": {"total": 10, "healthy_pct": 100, "unhealthy": 0},
        "deployments": {"total": 50, "success_rate": 98, "failed": 0},
        "alerts": {"total": 5, "critical": 0},
    })
    assert r["status"] == "green"
    assert r["score"] >= 90
    assert len(r["action_items"]) == 0

def test_red():
    r = build_command_center({
        "services": {"total": 10, "healthy_pct": 50, "unhealthy": 5},
        "deployments": {"success_rate": 60, "failed": 3},
        "alerts": {"critical": 5},
    })
    assert r["status"] == "red"
    assert len(r["action_items"]) == 3
