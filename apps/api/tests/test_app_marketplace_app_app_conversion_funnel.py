from app.services.app_marketplace_app_app_conversion_funnel import build_conversion_funnel

def test_funnel():
    steps = [
        {"name": "Visit Page", "count": 10000},
        {"name": "View Details", "count": 4000},
        {"name": "Click Install", "count": 1500},
        {"name": "Complete Install", "count": 1200},
    ]
    r = build_conversion_funnel(steps=steps)
    assert r["overall_conversion"] == 12.0
    assert r["steps"][0]["pct_of_total"] == 100.0
    assert r["worst_step"] == "Click Install"  # 60% drop

def test_empty():
    r = build_conversion_funnel(steps=[])
    assert r["overall_conversion"] == 0
