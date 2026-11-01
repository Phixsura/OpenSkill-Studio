from app.services.app_marketplace_app_app_app_app_app_pricing_comparison import build_pricing_comparison

def test_comparison():
    r = build_pricing_comparison()
    assert r["plan_count"] == 4
    assert r["feature_count"] == 9
    pro = next(p for p in r["plans"] if p["id"] == "pro")
    assert pro["recommended"]
    assert pro["price_display"] == "$29/mo"
    sso = next(f for f in r["features"] if f["name"] == "SSO/SAML")
    assert sso["values"]["enterprise"]["value"] is True
    assert sso["values"]["pro"]["value"] is False
