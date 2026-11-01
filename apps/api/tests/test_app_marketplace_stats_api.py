from app.services.app_marketplace_stats_api import get_public_stats, get_growth_metrics, build_stats_response

def test_stats():
    s = get_public_stats(
        apps=[{"status": "published", "category": "connector"}, {"status": "draft", "category": "analytics"}],
        developers=[{"verified": True}, {"verified": False}],
        installs=[{"status": "active"}, {"status": "uninstalled"}])
    assert s["published_apps"] == 1
    assert s["verified_developers"] == 1
    assert s["categories"] == 2

def test_growth():
    g = get_growth_metrics(current={"total_apps": 500}, previous={"total_apps": 400})
    assert g["total_apps"]["change"] == 100
    assert g["total_apps"]["change_pct"] == 25.0

def test_response():
    r = build_stats_response(stats={"published_apps": 100, "verified_developers": 50, "active_installs": 5000}, growth={})
    assert len(r["highlights"]) == 3
