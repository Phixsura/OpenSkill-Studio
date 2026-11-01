from app.services.app_marketplace_extension_ab_testing import (
    ABTestingService, ExperimentStatus,
)


def test_create_experiment():
    ab = ABTestingService()
    exp, msg = ab.create_experiment("exp-1", "ext-1", "Button Color", [
        {"name": "control", "weight": 50, "config": {"color": "blue"}},
        {"name": "variant_a", "weight": 50, "config": {"color": "green"}},
    ])
    assert exp is not None
    assert len(exp.variants) == 2


def test_invalid_weights():
    ab = ABTestingService()
    exp, msg = ab.create_experiment("exp-2", "ext-2", "Bad", [
        {"name": "a", "weight": 30},
        {"name": "b", "weight": 30},
    ])
    assert exp is None
    assert "sum to 100" in msg


def test_assign_variant():
    ab = ABTestingService()
    ab.create_experiment("exp-3", "ext-3", "Test", [
        {"name": "control", "weight": 50},
        {"name": "variant", "weight": 50},
    ])
    ab.start("exp-3")
    # Assign many users, should get both variants
    assignments = {ab.assign_variant("exp-3", f"user-{i}") for i in range(100)}
    assert "control" in assignments
    assert "variant" in assignments


def test_deterministic_assignment():
    ab = ABTestingService()
    ab.create_experiment("exp-4", "ext-4", "Det", [
        {"name": "a", "weight": 50}, {"name": "b", "weight": 50},
    ])
    ab.start("exp-4")
    first = ab.assign_variant("exp-4", "user-42")
    second = ab.assign_variant("exp-4", "user-42")
    assert first == second  # same user = same variant


def test_conversion_and_results():
    ab = ABTestingService()
    ab.create_experiment("exp-5", "ext-5", "CTA", [
        {"name": "control", "weight": 50}, {"name": "new_cta", "weight": 50},
    ])
    ab.start("exp-5")
    for i in range(20):
        ab.assign_variant("exp-5", f"u{i}")
    ab.record_conversion("exp-5", "new_cta")
    ab.record_conversion("exp-5", "new_cta")
    ab.record_conversion("exp-5", "control")
    results = ab.get_results("exp-5")
    assert results is not None
    assert len(results["variants"]) == 2


def test_lifecycle():
    ab = ABTestingService()
    ab.create_experiment("exp-6", "ext-6", "Test", [
        {"name": "a", "weight": 50}, {"name": "b", "weight": 50},
    ])
    ab.start("exp-6")
    assert ab.pause("exp-6") is True
    ab.start("exp-6")
    assert ab.complete("exp-6") is True
    assert ab._experiments["exp-6"].status == ExperimentStatus.COMPLETED
