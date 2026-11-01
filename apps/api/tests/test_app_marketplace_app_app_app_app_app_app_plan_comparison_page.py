from app.services.app_marketplace_app_app_app_app_app_app_plan_comparison_page import build_plan_comparison_page

def test_comparison():
    r = build_plan_comparison_page()
    assert r["plan_count"] == 4
    assert r["feature_count"] == 11
    pro = next(p for p in r["plans"] if p["id"] == "pro")
    assert pro.get("recommended")
    assert pro["price_display"] == "$29/mo"
