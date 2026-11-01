from app.services.app_marketplace_app_app_app_app_app_app_app_marketplace_summary import build_marketplace_summary

def test_summary():
    r = build_marketplace_summary()
    assert r["status"] == "FULLY OPERATIONAL"
    assert r["stats"]["total_apps"] == 500
    assert len(r["top_categories"]) == 5
    assert r["highlights"]["developer_satisfaction"] == 92
