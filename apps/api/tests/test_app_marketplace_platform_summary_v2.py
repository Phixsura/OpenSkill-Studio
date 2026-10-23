from app.services.app_marketplace_platform_summary_v2 import build_platform_summary_v2

def test_summary():
    s = build_platform_summary_v2(
        stats={"apps": 500, "developers": 100, "installs": 25000, "api_calls_today": 100000},
        health={"status": "healthy", "uptime": 99.99},
        growth={"apps_this_month": 15, "developers_this_month": 8, "installs_this_month": 2000},
        top_apps=[{"name": "App1"}], recent_activity=[{"type": "install"}])
    assert s["page_type"] == "platform_summary_v2"
    assert s["headline"]["total_apps"] == 500
    assert s["growth"]["apps_this_month"] == 15
    assert len(s["links"]) == 4
