from app.services.app_marketplace_app_developer_dashboard_v2 import build_dashboard_v2

def test_dashboard():
    d = build_dashboard_v2(
        developer={"display_name": "DevCo", "tier": "pro"},
        apps=[{"status": "published", "install_count": 500}, {"status": "draft", "install_count": 0}],
        inbox={"unread": 3}, health={"status": "healthy"}, revenue={"mrr": "$1,000"})
    assert d["page_type"] == "dashboard_v2"
    assert d["header"]["unread_messages"] == 3
    assert len(d["widgets"]) == 4  # includes revenue

def test_no_revenue():
    d = build_dashboard_v2(developer={"display_name": "X"}, apps=[], inbox={"unread": 0}, health={})
    assert len(d["widgets"]) == 3
