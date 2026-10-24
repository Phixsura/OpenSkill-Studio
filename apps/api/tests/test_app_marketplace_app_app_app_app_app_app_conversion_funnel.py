from app.services.app_marketplace_app_app_app_app_app_app_conversion_funnel import build_conversion_funnel

def test_funnel():
    steps = [
        {"name": "Visit", "count": 10000, "icon": "👁️"},
        {"name": "View App", "count": 3000, "icon": "📦"},
        {"name": "Click Install", "count": 800, "icon": "🔘"},
        {"name": "Complete Install", "count": 600, "icon": "✅"},
    ]
    r = build_conversion_funnel(steps=steps)
    assert r["step_count"] == 4
    assert r["overall_conversion"] == 6.0
    assert r["steps"][0]["drop_off_pct"] == 0
    assert r["steps"][1]["drop_off_pct"] == 70.0
