from app.services.app_marketplace_complete_platform_analytics_final import build_platform_analytics_final

def test_analytics():
    p = build_platform_analytics_final(
        apps=[{"name": "A", "category": "connector", "install_count": 500},
              {"name": "B", "category": "connector", "install_count": 200},
              {"name": "C", "category": "analytics", "install_count": 300}],
        developers=[{"display_name": "D1", "total_installs": 700}, {"display_name": "D2", "total_installs": 300}],
        installs=[{"id": "i1"}] * 1000, api_calls=500000,
        revenue={"mrr": 50000}, growth={"apps_this_month": 15})
    assert p["overview"]["total_apps"] == 3
    assert p["overview"]["mrr"] == 50000
    assert p["by_category"]["connector"] == 2
    assert p["top_apps"][0]["name"] == "A"
    assert len(p["charts"]) == 4
