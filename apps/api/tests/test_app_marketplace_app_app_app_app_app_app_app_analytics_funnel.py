from app.services.app_marketplace_app_app_app_app_app_app_app_analytics_funnel import build_funnel

def test_funnel():
    r = build_funnel([
        {"name": "Visit Page", "count": 10000},
        {"name": "View Details", "count": 3000},
        {"name": "Click Install", "count": 1500},
        {"name": "Complete Install", "count": 1200},
    ])
    assert r["total_steps"] == 4
    assert r["overall_conversion"] == 12.0
    assert r["steps"][0]["conversion"] == 100.0
    assert r["steps"][1]["drop_off"] == 7000
    assert r["worst_step"] == "View Details"
