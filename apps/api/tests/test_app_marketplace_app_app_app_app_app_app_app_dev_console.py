from app.services.app_marketplace_app_app_app_app_app_app_app_dev_console import build_dev_console

def test_console():
    r = build_dev_console(
        developer={"name": "Acme Corp", "plan": "pro", "verified": True},
        apps=[
            {"name": "App1", "installs": 5000, "rating": 4.5},
            {"name": "App2", "installs": 3000, "rating": 4.0},
        ],
        recent_deploys=[
            {"app": "App1", "version": "2.1.0", "status": "success", "time": "5m ago"},
        ],
        open_issues=3, api_calls_today=150000)
    assert r["developer"]["name"] == "Acme Corp"
    assert r["developer"]["verified"]
    assert r["apps_summary"]["total"] == 2
    assert r["apps_summary"]["total_installs"] == 8000
    assert r["api_display"] == "150,000"
    assert len(r["quick_actions"]) == 4
