from app.services.app_marketplace_app_app_ab_test_config import assign_variant, analyze_experiment

def test_assign_deterministic():
    variants = [{"id": "A", "name": "Control", "weight": 1}, {"id": "B", "name": "Test", "weight": 1}]
    r1 = assign_variant(experiment_id="exp1", user_id="u1", variants=variants)
    r2 = assign_variant(experiment_id="exp1", user_id="u1", variants=variants)
    assert r1["variant"] == r2["variant"]

def test_analyze():
    variants = [
        {"id": "A", "name": "Control", "impressions": 1000, "conversions": 50},
        {"id": "B", "name": "Test", "impressions": 1000, "conversions": 75},
    ]
    r = analyze_experiment(variants=variants)
    assert r["winner"] == "B"
    assert r["total_impressions"] == 2000
    assert r["results"][1]["conversion_rate"] == 7.5
