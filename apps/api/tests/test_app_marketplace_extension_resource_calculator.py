from app.services.app_marketplace_extension_resource_calculator import (
    ExtensionResourceCalculatorService, RecommendedTier,
)


def test_basic_estimate():
    svc = ExtensionResourceCalculatorService()
    est = svc.estimate(100, [])
    assert est.cpu_cores > 0
    assert est.memory_mb > 0
    assert est.recommended_tier in list(RecommendedTier)


def test_small_free_tier():
    svc = ExtensionResourceCalculatorService()
    est = svc.estimate(10, [])
    assert est.recommended_tier == RecommendedTier.FREE


def test_database_increases():
    svc = ExtensionResourceCalculatorService()
    without = svc.estimate(100, [])
    with_db = svc.estimate(100, [], has_database=True)
    assert with_db.memory_mb > without.memory_mb
    assert with_db.storage_mb > without.storage_mb


def test_ml_heavy():
    svc = ExtensionResourceCalculatorService()
    est = svc.estimate(1000, ["ml_inference"], has_database=True)
    assert est.cpu_cores > 2.0
    assert est.recommended_tier in (RecommendedTier.PRO, RecommendedTier.ENTERPRISE)


def test_cost_scales():
    svc = ExtensionResourceCalculatorService()
    small = svc.estimate(10, [])
    large = svc.estimate(10000, ["realtime", "ml_inference"], has_database=True)
    assert large.estimated_cost_cents > small.estimated_cost_cents
