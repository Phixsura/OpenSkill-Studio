from app.services.app_marketplace_app_ab_testing import (
    create_experiment, assign_variant, compute_results)

def test_create():
    r = create_experiment(app_id="a1", name="Title Test",
        variants=[{"id": "v1", "name": "A"}, {"id": "v2", "name": "B"}])
    assert r["status"] == "draft"
    assert len(r["variants"]) == 2

def test_too_few():
    r = create_experiment(app_id="a1", name="X", variants=[{"id": "v1", "name": "A"}])
    assert "error" in r

def test_assign():
    variants = [{"id": "v1", "name": "A"}, {"id": "v2", "name": "B"}]
    r = assign_variant(experiment_id="exp1", user_id="u1", variants=variants)
    assert r["variant_id"] in ("v1", "v2")

def test_results():
    variants = [{"id": "v1", "name": "A", "impressions": 1000, "conversions": 50},
                {"id": "v2", "name": "B", "impressions": 1000, "conversions": 70}]
    r = compute_results(variants=variants)
    assert r["winner"]["id"] == "v2"
    assert r["results"][1]["conversion_rate"] == 7.0
