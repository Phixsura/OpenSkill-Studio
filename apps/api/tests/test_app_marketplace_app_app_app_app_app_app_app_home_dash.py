from app.services.app_marketplace_app_app_app_app_app_app_app_home_dash import build_home_dashboard

def test_dashboard():
    r = build_home_dashboard(
        user={"name": "Alice", "plan": "pro"},
        apps=[{"name": "A", "installs": 100}, {"name": "B", "installs": 500}],
        notifications=5, health_score=95,
        recent_events=[{"title": "Deploy complete", "type": "deploy"}])
    assert "Alice" in r["greeting"]
    assert r["plan"] == "pro"
    assert len(r["stats"]) == 3
    assert r["top_apps"][0]["name"] == "B"
    assert len(r["quick_actions"]) == 4
