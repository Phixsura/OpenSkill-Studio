from app.services.app_marketplace_app_app_app_app_app_app_app_rate_plan import get_plan, compare_plans, can_use_feature

def test_plan():
    p = get_plan("pro")
    assert p["price"] == 99
    assert p["price_display"] == "$99/mo"
    assert "sso" in p["features"]

def test_enterprise():
    p = get_plan("enterprise")
    assert p["is_unlimited"]
    assert p["price_display"] == "Custom"

def test_compare():
    plans = compare_plans()
    assert len(plans) == 4

def test_feature():
    assert can_use_feature("pro", "sso")
    assert not can_use_feature("free", "sso")
