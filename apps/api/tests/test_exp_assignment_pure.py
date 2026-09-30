"""Pure-logic tests for the ADR-017 §6 bucketing core. No DB, no app.

The assignment decision core is deterministic arithmetic over SHA-256 —
uniformity, salt independence, ramp monotonicity and boundary behavior are
all testable exhaustively or statistically without infrastructure.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from app.experiments.schemas import ExperimentSpec, PopulationSpec
from app.experiments.services.assignment import (
    BUCKET_SPACE,
    bucket,
    evaluate_population,
    holdout_roll,
    in_ramp,
    pick_variant,
    variant_roll,
)


def _spec(weights: list[tuple[str, int, bool]]) -> ExperimentSpec:
    return ExperimentSpec.model_validate(
        {
            "hypothesis": "x" * 10,
            "unit_type": "user",
            "variants": [
                {"key": k, "name": k, "weight_bp": w, "is_control": c}
                for k, w, c in weights
            ],
            "metrics": {"primary": ["m"]},
        }
    )


# ── Determinism & uniformity ─────────────────────────────────────────


def test_hash_golden_vectors():
    """Pinned outputs for fixed inputs — kills any silent change to the
    digest-slice width, parse base or salt layout (a changed constant would
    re-randomize EVERY live experiment on deploy)."""
    assert bucket("layer-golden", "user", "unit-42") == 8322
    assert holdout_roll("exp-golden", "user", "unit-42") == 8783
    assert variant_roll("exp-golden", "saltgold", "user", "unit-42") == 2885


def test_population_eq_empty_values_fail_closed():
    """eq with an empty values list must be False, never an IndexError."""
    assert not evaluate_population(
        _pop([{"field": "cohort_id", "op": "eq", "values": []}]), {"cohort_id": "c1"}
    )


def test_bucket_deterministic():
    assert bucket("layer-a", "user", "u1") == bucket("layer-a", "user", "u1")
    assert 0 <= bucket("layer-a", "user", "u1") < BUCKET_SPACE


def test_bucket_uniformity_chi_square():
    """20k units over 10 deciles — chi-square must be unsuspicious.
    Critical value for df=9 at p=0.001 is 27.88."""
    n = 20_000
    counts = [0] * 10
    for i in range(n):
        counts[bucket("layer-uni", "user", f"unit-{i}") * 10 // BUCKET_SPACE] += 1
    expected = n / 10
    chi2 = sum((c - expected) ** 2 / expected for c in counts)
    assert chi2 < 27.88, f"bucket distribution suspicious: chi2={chi2:.2f} {counts}"


def test_salt_independence_layer_vs_variant():
    """Within a narrow layer-bucket band, the variant roll must still split
    evenly — correlated hashes were a classic platform incident class."""
    in_band = [
        f"unit-{i}"
        for i in range(60_000)
        if bucket("layer-x", "user", f"unit-{i}") < 1000  # ~6k units
    ]
    assert len(in_band) > 4000
    low_roll = sum(1 for u in in_band if variant_roll("exp-x", "salt1234", "user", u) < 5000)
    ratio = low_roll / len(in_band)
    assert 0.47 < ratio < 0.53, f"variant roll correlated with layer bucket: {ratio:.3f}"


def test_holdout_salt_independent_of_variant_roll():
    units = [f"u{i}" for i in range(30_000)]
    held = [u for u in units if holdout_roll("exp-h", "user", u) < 500]  # 5% holdout
    assert 0.04 < len(held) / len(units) < 0.06
    # Remaining population's variant split is not skewed by holdout removal
    rest = [u for u in units if u not in set(held)]
    low = sum(1 for u in rest if variant_roll("exp-h", "s", "user", u) < 5000)
    assert 0.48 < low / len(rest) < 0.52


# ── Variant picking ──────────────────────────────────────────────────


def test_pick_variant_boundaries():
    spec = _spec([("a", 1, True), ("b", 9999, False)])
    assert pick_variant(spec, 0) == "a"
    assert pick_variant(spec, 1) == "b"
    assert pick_variant(spec, 9999) == "b"


def test_pick_variant_three_way_split():
    spec = _spec([("a", 2000, True), ("b", 3000, False), ("c", 5000, False)])
    assert pick_variant(spec, 1999) == "a"
    assert pick_variant(spec, 2000) == "b"
    assert pick_variant(spec, 4999) == "b"
    assert pick_variant(spec, 5000) == "c"


# ── Ramp ─────────────────────────────────────────────────────────────


def test_ramp_zero_admits_nobody_and_full_admits_slice():
    for b in (0, 1, 4999, 9999):
        assert not in_ramp(bucket_value=b, slice_start=0, slice_end=9999, ramp_bp=0)
        assert in_ramp(bucket_value=b, slice_start=0, slice_end=9999, ramp_bp=10_000)


def test_ramp_half_slice_integer_math():
    # slice [100, 199], ramp 50% → local 0..49 in, 50..99 out
    assert in_ramp(bucket_value=149, slice_start=100, slice_end=199, ramp_bp=5000)
    assert not in_ramp(bucket_value=150, slice_start=100, slice_end=199, ramp_bp=5000)


@settings(max_examples=200)
@given(
    b=st.integers(min_value=0, max_value=9999),
    start=st.integers(min_value=0, max_value=9000),
    width=st.integers(min_value=1, max_value=999),
    r1=st.integers(min_value=0, max_value=10_000),
    r2=st.integers(min_value=0, max_value=10_000),
)
def test_ramp_monotonicity_property(b, start, width, r1, r2):
    """A unit admitted at ramp r stays admitted at every r' >= r (no unit
    ever loses its experience on a ramp-up — the ITT guarantee)."""
    end = start + width - 1
    lo, hi = sorted((r1, r2))
    if in_ramp(bucket_value=b, slice_start=start, slice_end=end, ramp_bp=lo):
        assert in_ramp(bucket_value=b, slice_start=start, slice_end=end, ramp_bp=hi)


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=30), st.text(min_size=1, max_size=30))
def test_hash_stability_property(key, unit):
    assert bucket(key, "user", unit) == bucket(key, "user", unit)
    assert variant_roll(key, "s", "user", unit) == variant_roll(key, "s", "user", unit)


# ── Population rules (fail-closed) ───────────────────────────────────


def _pop(rules=None, exclusions=None) -> PopulationSpec:
    return PopulationSpec.model_validate(
        {"rules": rules or [], "exclusions": exclusions or []}
    )


def test_population_empty_is_everyone():
    assert evaluate_population(_pop(), {})


def test_population_ops():
    ctx = {"cohort_id": "c1", "plan_tier": "pro", "signup_after": 5}
    assert evaluate_population(_pop([{"field": "cohort_id", "op": "eq", "values": ["c1"]}]), ctx)
    assert evaluate_population(_pop([{"field": "plan_tier", "op": "in", "values": ["pro", "max"]}]), ctx)
    assert evaluate_population(_pop([{"field": "plan_tier", "op": "not_in", "values": ["free"]}]), ctx)
    assert evaluate_population(_pop([{"field": "signup_after", "op": "gte", "values": [5]}]), ctx)
    assert not evaluate_population(_pop([{"field": "signup_after", "op": "gte", "values": [6]}]), ctx)
    assert evaluate_population(_pop([{"field": "signup_after", "op": "lte", "values": [5]}]), ctx)
    assert evaluate_population(_pop([{"field": "cohort_id", "op": "exists", "values": []}]), ctx)


def test_population_missing_field_fails_closed():
    """No accidental enrollment of units we cannot evaluate."""
    assert not evaluate_population(
        _pop([{"field": "cohort_id", "op": "eq", "values": ["c1"]}]), {}
    )
    assert not evaluate_population(
        _pop([{"field": "signup_after", "op": "gte", "values": ["not-a-number"]}]),
        {"signup_after": "also-bad"},
    )


def test_population_exclusion_wins():
    ctx = {"cohort_id": "c1", "plan_tier": "free"}
    assert not evaluate_population(
        _pop(
            rules=[{"field": "cohort_id", "op": "eq", "values": ["c1"]}],
            exclusions=[{"field": "plan_tier", "op": "eq", "values": ["free"]}],
        ),
        ctx,
    )


# ── Switchback day-variant (v2 batch 11, §4.5) ───────────────────────


def test_switchback_variant_deterministic_per_day_and_rotates():
    from datetime import UTC, datetime, timedelta

    from app.experiments.schemas import ExperimentSpec
    from app.experiments.services.assignment import switchback_variant

    spec = ExperimentSpec.model_validate({
        "hypothesis": "switchback determinism",
        "unit_type": "user",
        "design": "switchback",
        "switchback": {"switch_unit": "platform_day", "window_minutes": 1440},
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {"primary": ["exposure_rate"],
                    "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                    "threshold": 100.0}]},
    })
    base_at = datetime(2026, 9, 1, 0, 30, tzinfo=UTC)
    # same 1440-minute window (epoch-aligned) → same variant
    a = switchback_variant("sb-exp", "saltgold", spec, base_at)
    assert a == switchback_variant("sb-exp", "saltgold", spec,
                                   base_at + timedelta(hours=11))
    assert a in ("control", "treatment")
    # across 30 days both variants appear (weights 50/50)
    seen = {
        switchback_variant("sb-exp", "saltgold", spec, base_at + timedelta(days=d))
        for d in range(30)
    }
    assert seen == {"control", "treatment"}
    # a different salt yields a different schedule somewhere in the month
    other = [
        switchback_variant("sb-exp", "othersalt", spec, base_at + timedelta(days=d))
        for d in range(30)
    ]
    mine = [
        switchback_variant("sb-exp", "saltgold", spec, base_at + timedelta(days=d))
        for d in range(30)
    ]
    assert other != mine
