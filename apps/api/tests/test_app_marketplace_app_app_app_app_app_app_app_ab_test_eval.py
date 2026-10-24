from app.services.app_marketplace_app_app_app_app_app_app_app_ab_test_eval import evaluate_experiment

def test_significant():
    r = evaluate_experiment(
        {"visitors": 10000, "conversions": 500},
        {"visitors": 10000, "conversions": 700})
    assert r["significant"]
    assert r["winner"] == "variant"
    assert r["lift_pct"] > 0

def test_inconclusive():
    r = evaluate_experiment(
        {"visitors": 100, "conversions": 5},
        {"visitors": 100, "conversions": 6})
    assert r["winner"] == "inconclusive"
