from app.services.app_marketplace_pricing_page import build_pricing_page

def test_monthly():
    p = build_pricing_page(current_plan="free")
    assert len(p["plans"]) == 4
    assert p["plans"][0]["is_current"]
    assert p["plans"][2]["highlighted"]
    assert p["trial_days"] == 14

def test_annual():
    p = build_pricing_page(annual=True)
    assert p["annual"]
    pro = next(x for x in p["plans"] if x["id"] == "pro")
    assert pro["savings_pct"] == 17

def test_faq():
    p = build_pricing_page()
    assert len(p["faq"]) >= 4
