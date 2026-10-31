from app.services.app_marketplace_app_app_app_app_app_app_app_ab_test_results import analyze_ab_test

def test_ab_significant():
    r = analyze_ab_test(control_visitors=5000, control_conversions=200,
                         variant_visitors=5000, variant_conversions=280)
    assert r["control"]["rate"] == 4.0
    assert r["variant"]["rate"] == 5.6
    assert r["lift"] == 40.0
    assert r["significant"]
    assert r["winner"] == "variant"

def test_ab_not_significant():
    r = analyze_ab_test(control_visitors=50, control_conversions=5,
                         variant_visitors=50, variant_conversions=6)
    assert not r["significant"]
    assert r["winner"] == "none"
