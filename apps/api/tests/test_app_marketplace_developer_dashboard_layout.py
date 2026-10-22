from app.services.app_marketplace_developer_dashboard_layout import build_dashboard_layout

def test_layout():
    l = build_dashboard_layout(
        developer={"display_name": "DevCo"},
        apps=[{"status": "published", "install_count": 100, "review_status": "approved"},
              {"status": "draft", "install_count": 0, "review_status": "pending"}],
        notifications_count=3)
    assert l["developer_name"] == "DevCo"
    assert len(l["sidebar"]) == 5
    assert l["quick_stats"]["published"] == 1
    assert l["quick_stats"]["total_installs"] == 100
    assert l["quick_stats"]["pending_reviews"] == 1
    assert l["notifications_count"] == 3

def test_empty():
    l = build_dashboard_layout(developer={"display_name": "New"}, apps=[], notifications_count=0)
    assert l["quick_stats"]["total_apps"] == 0
