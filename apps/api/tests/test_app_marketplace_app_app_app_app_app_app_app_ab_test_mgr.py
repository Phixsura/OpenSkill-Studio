from app.services.app_marketplace_app_app_app_app_app_app_app_ab_test_mgr import (
    create_experiment, assign_variant, evaluate_results,
)

def test_experiment():
    exp = create_experiment("button_color", [{"name": "red", "weight": 1}, {"name": "blue", "weight": 1}])
    assert exp["variant_count"] == 2
    assert exp["variants"][0]["weight"] == 50.0

def test_assign():
    exp = create_experiment("test", [{"name": "A", "weight": 1}, {"name": "B", "weight": 1}])
    v = assign_variant(exp, "user123")
    assert v in ("A", "B")

def test_evaluate():
    r = evaluate_results({
        "A": {"views": 1000, "conversions": 50},
        "B": {"views": 1000, "conversions": 80},
    })
    assert r["winner"] == "B"
    assert r["best_rate"] == 8.0
