from app.services.app_marketplace_app_ab_testing import create_experiment, assign_variant, compute_experiment_results

def test_create():
    r = create_experiment(app_id="a1", name="Title test",
                           variants=[{"id": "a", "name": "Original"}, {"id": "b", "name": "New"}])
    assert len(r["variants"]) == 2
    assert r["status"] == "draft"

def test_too_few():
    r = create_experiment(app_id="a1", name="X", variants=[{"id": "a"}])
    assert r["error"]

def test_assign_deterministic():
    v1 = assign_variant(user_id="u1", experiment_id="exp1", variants=[{"id": "a", "weight": 50}, {"id": "b", "weight": 50}])
    v2 = assign_variant(user_id="u1", experiment_id="exp1", variants=[{"id": "a", "weight": 50}, {"id": "b", "weight": 50}])
    assert v1["variant_id"] == v2["variant_id"]

def test_results():
    variants = [{"id": "a", "name": "A", "views": 1000, "conversions": 50},
                {"id": "b", "name": "B", "views": 1000, "conversions": 80}]
    r = compute_experiment_results(variants=variants)
    assert r["winner"]["id"] == "b"
