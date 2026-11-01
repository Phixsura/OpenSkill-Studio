from app.services.app_marketplace_app_marketplace_analytics_v2 import compute_marketplace_kpis, compute_category_breakdown, identify_growth_opportunities

def test_kpis():
    apps = [{"status": "published"}, {"status": "draft"}]
    installs = [{"status": "active"}, {"status": "active"}, {"status": "uninstalled"}]
    reviews = [{"rating": 5}, {"rating": 4}]
    k = compute_marketplace_kpis(apps=apps, installs=installs, reviews=reviews)
    assert k["published_apps"] == 1
    assert k["active_installs"] == 2
    assert k["avg_rating"] == 4.5

def test_categories():
    apps = [{"category": "connector", "install_count": 100}, {"category": "connector", "install_count": 200},
            {"category": "analytics", "install_count": 50}]
    c = compute_category_breakdown(apps=apps)
    assert c[0]["category"] == "connector"
    assert c[0]["installs"] == 300

def test_opportunities():
    tips = identify_growth_opportunities(kpis={"published_apps": 10, "total_apps": 100, "churn_rate": 30, "avg_rating": 3.0})
    assert len(tips) == 3
