from app.services.app_marketplace_hero_stats import build_hero_stats

def test_stats():
    s = build_hero_stats(total_apps=100, total_installs=5000, total_developers=20, total_executions=100000)
    assert len(s) == 4
    assert s[0]["label"] == "Apps"
    assert s[0]["value"] == 100
