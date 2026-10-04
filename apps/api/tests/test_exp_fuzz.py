"""Hypothesis fuzz layer for the experimentation cores (ADR-017 §18 round 7).

Contract under fuzz: every untrusted-input surface either returns a normal
value or raises a TYPED AppError — never any other exception. Pure decision
functions are total over their domains.
"""

import math

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.exceptions import AppError
from app.experiments.schemas import PopulationSpec
from app.experiments.services.analysis import (
    benjamini_hochberg,
    msprt_always_valid_p,
    obrien_fleming_boundary,
)
from app.experiments.services.assignment import evaluate_population
from app.experiments.services.experiments import ExperimentService, canonical_spec_hash
from app.experiments.services.guardrails import GuardrailService

_FUZZ = settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)

# JSON-ish scalar/compound values (no NaN in json.dumps paths — tested apart)
_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(10**12), max_value=10**12),
    st.floats(allow_nan=False, allow_infinity=False, width=32),
    st.text(max_size=40),
)
_json_values = st.recursive(
    _scalars,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(st.text(max_size=12), children, max_size=4),
    ),
    max_leaves=12,
)


# ── Spec validation: parsed or typed AppError, nothing else ──────────


@_FUZZ
@given(spec=st.dictionaries(st.text(max_size=24), _json_values, max_size=8))
def test_validate_spec_total_over_garbage(spec):
    svc = ExperimentService(None)
    try:
        svc.validate_spec(spec, domain="learning", risk_class="medium")
    except AppError as e:
        assert e.status_code in (404, 409, 422)
        assert e.code.isupper()


@_FUZZ
@given(
    hypothesis_text=st.text(min_size=10, max_size=200),
    field=st.text(min_size=1, max_size=30),
    values=st.lists(_scalars.filter(lambda v: not isinstance(v, (dict, list))), max_size=5),
)
def test_validate_spec_population_rules_total(hypothesis_text, field, values):
    """Arbitrary rule fields/values: either a valid spec or a typed 422 —
    the ethics gate must never crash on adversarial field names."""
    spec = {
        "hypothesis": hypothesis_text,
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {"primary": ["m"]},
        "population": {"rules": [{"field": field, "op": "eq", "values": values}]},
    }
    try:
        ExperimentService(None).validate_spec(spec, domain="learning", risk_class="low")
    except AppError as e:
        assert e.code in ("EXPERIMENT_SPEC_INVALID", "EXPERIMENT_FORBIDDEN_TARGETING")
        assert e.status_code == 422


# ── Population evaluation is total: bool, never an exception ─────────

_ops = st.sampled_from(["eq", "in", "not_in", "gte", "lte", "exists"])


_rule_values = st.lists(
    st.one_of(
        st.booleans(),
        st.integers(min_value=-(10**9), max_value=10**9),
        st.floats(allow_nan=False, allow_infinity=False, width=32),
        st.text(max_size=20),
    ),
    max_size=4,
)


@_FUZZ
@given(
    op=_ops,
    values=_rule_values,  # schema domain (None etc. is a typed 422 — covered above)
    context=st.dictionaries(st.text(max_size=12), _json_values, max_size=5),
    field=st.sampled_from(["cohort_id", "plan_tier", "signup_after", "locale"]),
)
def test_evaluate_population_total(op, values, context, field):
    population = PopulationSpec.model_validate(
        {"rules": [{"field": field, "op": op, "values": values}]}
    )
    result = evaluate_population(population, context)
    assert isinstance(result, bool)


# ── Canonical hash: stable, order-independent, total on JSONables ────


@_FUZZ
@given(payload=st.dictionaries(st.text(max_size=12), _json_values, max_size=6))
def test_canonical_hash_stable_and_order_free(payload):
    h1 = canonical_spec_hash(payload)
    h2 = canonical_spec_hash(dict(reversed(list(payload.items()))))
    assert h1 == h2
    assert len(h1) == 64


# ── Guardrail observed scalar: float or None, never an exception ─────


@_FUZZ
@given(
    kind=st.sampled_from(["binary", "rate", "continuous", "time_to_event"]),
    aggregate=st.sampled_from([None, "rate", "sum", "mean"]),
    combined=st.dictionaries(
        st.sampled_from(["n", "numerator", "denominator", "sum_value", "sum_sq"]),
        st.one_of(
            st.none(),
            st.integers(min_value=-(10**9), max_value=10**9),
            st.floats(allow_nan=False, allow_infinity=False),
        ),
        max_size=5,
    ),
)
def test_observed_total(kind, aggregate, combined):
    from types import SimpleNamespace

    spec = {} if aggregate is None else {"guardrail_aggregate": aggregate}
    definition = SimpleNamespace(kind=kind, spec=spec)
    out = GuardrailService._observed(definition, combined)
    assert out is None or isinstance(out, float)
    if out is not None:
        assert math.isfinite(out)


# ── Sequential helpers stay in range under fuzz ──────────────────────


@_FUZZ
@given(z=st.floats(allow_nan=False, allow_infinity=False, min_value=-40, max_value=40),
       tau=st.floats(min_value=0.05, max_value=10))
def test_msprt_p_in_unit_interval(z, tau):
    p = msprt_always_valid_p(z, tau=tau)
    assert 0.0 <= p <= 1.0


@_FUZZ
@given(k=st.integers(min_value=1, max_value=50), n=st.integers(min_value=1, max_value=50))
def test_of_boundary_positive_and_monotone(k, n):
    if k > n:
        return
    b = obrien_fleming_boundary(k, n)
    assert b > 0
    if k < n:
        assert b >= obrien_fleming_boundary(k + 1, n)


@_FUZZ
@given(
    ps=st.dictionaries(
        st.text(min_size=1, max_size=8),
        st.floats(min_value=0, max_value=1, allow_nan=False),
        max_size=8,
    )
)
def test_bh_total_and_monotone(ps):
    out = benjamini_hochberg(ps)
    assert set(out) == set(ps)
    # Monotone: if a p-value passes, every smaller one passes too
    passed = sorted(p for key, p in ps.items() if out[key])
    failed = sorted(p for key, p in ps.items() if not out[key])
    if passed and failed:
        assert max(passed) <= min(failed) + 1e-12


# ── Round-10 cores: totality contracts ───────────────────────────────


@given(
    strata=st.lists(
        st.tuples(
            st.floats(allow_nan=True, allow_infinity=True),
            st.floats(allow_nan=True, allow_infinity=True),
        ),
        max_size=20,
    )
)
@settings(max_examples=300, suppress_health_check=[HealthCheck.too_slow])
def test_pool_stratified_total(strata):
    from app.experiments.services.analysis import pool_stratified

    result = pool_stratified(strata)
    if result is not None:
        assert math.isfinite(result["effect"])
        assert math.isfinite(result["se"]) and result["se"] > 0
        assert 0.0 <= result["p"] <= 1.0
        assert result["ci"][0] <= result["effect"] <= result["ci"][1]
        assert result["strata"] >= 2


@given(
    arms=st.dictionaries(
        st.text(min_size=1, max_size=8),
        st.tuples(
            st.floats(min_value=-1e6, max_value=1e6),
            st.floats(min_value=-1e6, max_value=1e6),
        ),
        max_size=6,
    )
)
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_thompson_weights_total(arms):
    from app.experiments.services.analysis import thompson_weights

    # negative/corrupt arm counts: the fn must filter, not crash
    result = thompson_weights(arms, draws=50)
    if result is not None:
        assert sum(result["suggested_weights_bp"].values()) == 10_000
        assert all(0.0 <= p <= 1.0 for p in result["p_best"].values())
        assert abs(sum(result["p_best"].values()) - 1.0) < 1e-9


@given(
    x=st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e308),
    df=st.integers(min_value=1, max_value=200),
)
@settings(max_examples=300)
def test_chi2_sf_in_unit_interval(x, df):
    from app.experiments.services.analysis import chi2_sf

    p = chi2_sf(x, df)
    assert 0.0 <= p <= 1.0


@given(
    key=st.text(min_size=1, max_size=40),
    salt=st.text(min_size=1, max_size=16),
    minutes=st.integers(min_value=0, max_value=10**9),
    window=st.integers(min_value=5, max_value=10_080),
)
@settings(max_examples=200)
def test_switchback_variant_total_and_stable(key, salt, minutes, window):
    from datetime import UTC, datetime, timedelta

    from app.experiments.schemas import ExperimentSpec
    from app.experiments.services.assignment import switchback_variant

    spec = ExperimentSpec.model_validate({
        "hypothesis": "switchback fuzz totality",
        "unit_type": "user",
        "design": "switchback",
        "switchback": {"switch_unit": "x", "window_minutes": window},
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {"primary": ["exposure_rate"],
                    "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                    "threshold": 100.0}]},
    })
    at = datetime(2020, 1, 1, tzinfo=UTC) + timedelta(minutes=minutes)
    v = switchback_variant(key, salt, spec, at)
    assert v in ("control", "treatment")
    assert v == switchback_variant(key, salt, spec, at)  # stable


_arm_floats = st.floats(min_value=-1e12, max_value=1e12)


@given(
    control=st.fixed_dictionaries({
        "n": st.integers(min_value=0, max_value=1000),
        "sum": _arm_floats, "sum_sq": _arm_floats,
        "cov_sum": _arm_floats, "cov_sum_sq": _arm_floats,
        "cov_xy_sum": _arm_floats,
    }),
    treatment=st.fixed_dictionaries({
        "n": st.integers(min_value=0, max_value=1000),
        "sum": _arm_floats, "sum_sq": _arm_floats,
        "cov_sum": _arm_floats, "cov_sum_sq": _arm_floats,
        "cov_xy_sum": _arm_floats,
    }),
)
@settings(max_examples=300, suppress_health_check=[HealthCheck.too_slow])
def test_did_estimate_total(control, treatment):
    from app.experiments.services.analysis import did_estimate

    result = did_estimate(control, treatment)
    if result is not None:
        assert math.isfinite(result["effect"])
        assert math.isfinite(result["se"]) and result["se"] >= 0.0
        if result["p"] is not None:
            assert 0.0 <= result["p"] <= 1.0
        assert result["ci"][0] <= result["effect"] <= result["ci"][1]


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
@given(
    hist=st.dictionaries(
        st.one_of(
            st.just("__zero__"), st.just("__neg__"),
            st.integers(min_value=-25, max_value=50).map(str),
            st.text(max_size=6),
        ),
        st.one_of(st.integers(min_value=-5, max_value=10_000), st.just(0)),
        max_size=12,
    ),
    p=st.floats(min_value=-0.5, max_value=1.5, allow_nan=False),
)
def test_fuzz_histogram_quantile_total(hist, p):
    """§4.14 under fire: stored JSONB can rot (old rows, manual edits) —
    histogram_quantile must return None or a finite, ordered read for ANY
    string->int mapping, never raise."""
    import math as _math

    from app.experiments.services.analysis import histogram_quantile

    try:
        out = histogram_quantile(hist, p)
    except (ValueError, TypeError):
        # non-numeric bucket keys are a programming error upstream; the
        # function may refuse them loudly but only with these types
        return
    if out is None:
        return
    assert _math.isfinite(out["estimate"]) and out["estimate"] >= 0.0
    lo, hi = out["ci"]
    assert lo <= out["estimate"] <= hi
    assert out["n"] >= 2


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
@given(quantiles=st.one_of(
    st.none(),
    st.text(max_size=6),
    st.integers(),
    st.lists(st.one_of(st.floats(allow_nan=True, allow_infinity=True),
                       st.text(max_size=3), st.none()), max_size=6),
    st.dictionaries(st.text(max_size=3), st.integers(), max_size=3),
))
def test_fuzz_validate_quantiles_total(quantiles):
    """The quantiles knob validator is TOTAL over arbitrary garbage: it
    returns None (accept) or raises the typed 422 — nothing else."""
    from app.exceptions import AppError
    from app.experiments.services.metrics import _validate_quantiles

    try:
        _validate_quantiles(quantiles, "continuous")
    except AppError as exc:
        assert exc.status_code == 422
