from app.services.app_marketplace_app_app_app_app_app_app_app_quick_stats import compute_quick_stats

def test_stats():
    r = compute_quick_stats(total_apps=250, total_developers=1500,
                             api_calls_today=2500000, active_deployments=3,
                             open_incidents=0, uptime_pct=99.95)
    assert len(r["stats"]) == 6
    assert r["stats"][0]["display"] == "250"
    assert r["stats"][2]["display"] == "2,500,000"
    assert r["stats"][5]["icon"] == "🟢"
