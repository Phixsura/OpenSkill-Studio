from app.services.app_marketplace_app_app_ab_test_results import analyze_ab_test

def test_variant_wins():
    r = analyze_ab_test(
        control={"visitors": 5000, "conversions": 200},
        variant={"visitors": 5000, "conversions": 300})
    assert r["winner"] == "variant"
    assert r["lift_pct"] > 0
    assert r["significant"]
    assert "Promote variant" in r["recommendation"]

def test_not_significant():
    r = analyze_ab_test(
        control={"visitors": 50, "conversions": 5},
        variant={"visitors": 50, "conversions": 6})
    assert not r["significant"]
    assert "Continue" in r["recommendation"]

def test_control_wins():
    r = analyze_ab_test(
        control={"visitors": 5000, "conversions": 400},
        variant={"visitors": 5000, "conversions": 200})
    assert r["winner"] == "control"
    assert r["lift_pct"] < 0
