"""Pure-logic tests for ADR-017 exp01: spec validation, ethics gates and the
lifecycle state machine. No DB, no app — the decision cores are pure.
"""

import pytest

from app.exceptions import AppError
from app.experiments.security import (
    EXPERIMENT_STATUSES,
    FORBIDDEN_TARGETING_KEYS,
    PROMOTION_TARGET_TYPES,
    check_bandit_gate,
    check_targeting_field,
)
from app.experiments.services.experiments import (
    _ALLOWED,
    ExperimentService,
    canonical_spec_hash,
)


def _spec(**overrides) -> dict:
    base = {
        "hypothesis": "Rubric wording B reduces revision count safely",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "Current", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "New", "weight_bp": 5000},
        ],
        "metrics": {"primary": ["project_approval_rate"]},
    }
    base.update(overrides)
    return base


def _validate(spec: dict, *, domain: str = "learning", risk_class: str = "medium"):
    return ExperimentService(None).validate_spec(spec, domain=domain, risk_class=risk_class)


# ── Spec validation ─────────────────────────────────────────────────


def test_valid_minimal_spec_parses():
    parsed = _validate(_spec())
    assert parsed.design == "parallel"
    assert parsed.sequential == "msprt"
    assert parsed.analysis_type == "randomized"


def test_weights_must_sum_to_10000():
    bad = _spec(
        variants=[
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "t", "name": "T", "weight_bp": 4000},
        ]
    )
    with pytest.raises(AppError) as e:
        _validate(bad)
    assert e.value.code == "EXPERIMENT_SPEC_INVALID"
    assert "10000" in e.value.message


def test_exactly_one_control():
    bad = _spec(
        variants=[
            {"key": "a", "name": "A", "weight_bp": 5000, "is_control": True},
            {"key": "b", "name": "B", "weight_bp": 5000, "is_control": True},
        ]
    )
    with pytest.raises(AppError):
        _validate(bad)


def test_duplicate_variant_keys_rejected():
    bad = _spec(
        variants=[
            {"key": "same", "name": "A", "weight_bp": 5000, "is_control": True},
            {"key": "same", "name": "B", "weight_bp": 5000},
        ]
    )
    with pytest.raises(AppError):
        _validate(bad)


def test_unknown_spec_field_rejected():
    # extra="forbid" — a typo'd field must 422, never silently drop (R300)
    with pytest.raises(AppError):
        _validate(_spec(hypothesys="typo"))


def test_switchback_requires_config_and_vice_versa():
    with pytest.raises(AppError):
        _validate(_spec(design="switchback"))
    with pytest.raises(AppError):
        _validate(_spec(switchback={"switch_unit": "org"}))
    ok = _validate(_spec(design="switchback", switchback={"switch_unit": "org"}))
    assert ok.switchback.window_minutes == 60


def test_washout_must_be_shorter_than_window():
    """Defect #44: washout >= window folds EVERY snapshot window to zero —
    the experiment runs forever collecting nothing. Rejected at the spec
    boundary; the exact == boundary is the dangerous one (a whole window of
    washout leaves a zero-length effective window)."""
    for washout in (60, 61, 1440):
        with pytest.raises(AppError):
            _validate(_spec(design="switchback", switchback={
                "switch_unit": "org", "window_minutes": 60,
                "washout_minutes": washout,
            }))
    ok = _validate(_spec(design="switchback", switchback={
        "switch_unit": "org", "window_minutes": 60, "washout_minutes": 59,
    }))
    assert ok.switchback.washout_minutes == 59


def test_aa_probe_n_is_bounded_at_the_route():
    """Defect #45: aa_probe is a synchronous hash loop on the event loop —
    the route must clamp n (an unbounded admin typo stalls the API)."""
    import inspect

    from app.experiments.api.layers import layer_aa_probe

    param = inspect.signature(layer_aa_probe).parameters["n"]
    meta = param.default  # fastapi Query carries the constraint metadata
    constraints = {
        type(m).__name__.lower(): getattr(m, "ge", getattr(m, "le", None))
        for m in getattr(meta, "metadata", [])
    }
    assert constraints.get("ge") == 100
    assert constraints.get("le") == 50_000


def test_nonfinite_guardrail_threshold_rejected():
    bad = _spec(
        metrics={
            "primary": ["x"],
            "guardrails": [{"metric_key": "cost_usd", "op": "lte", "threshold": float("inf")}],
        }
    )
    with pytest.raises(AppError):
        _validate(bad)


# ── Ethics gates (ADR-017 §2) ───────────────────────────────────────


@pytest.mark.parametrize("field", sorted(FORBIDDEN_TARGETING_KEYS))
def test_forbidden_targeting_keys_all_rejected(field):
    with pytest.raises(AppError) as e:
        check_targeting_field(field)
    assert e.value.code == "EXPERIMENT_FORBIDDEN_TARGETING"


def test_forbidden_targeting_case_insensitive():
    with pytest.raises(AppError) as e:
        check_targeting_field("  Gender ")
    assert e.value.code == "EXPERIMENT_FORBIDDEN_TARGETING"


def test_unknown_population_field_rejected():
    with pytest.raises(AppError) as e:
        check_targeting_field("favorite_color")
    assert e.value.code == "EXPERIMENT_SPEC_INVALID"


def test_population_rule_targeting_enforced_via_spec():
    bad = _spec(
        population={"rules": [{"field": "gender", "op": "eq", "values": ["x"]}]}
    )
    with pytest.raises(AppError) as e:
        _validate(bad)
    assert e.value.code == "EXPERIMENT_FORBIDDEN_TARGETING"


def test_bandit_gate_domain_and_risk():
    check_bandit_gate(domain="marketplace", risk_class="low", allocation_mode="bandit")
    for domain, risk in [
        ("learning", "low"),
        ("matching", "low"),
        ("talent_flow", "low"),
        ("marketplace", "medium"),
        ("marketplace", "high"),
    ]:
        with pytest.raises(AppError) as e:
            check_bandit_gate(domain=domain, risk_class=risk, allocation_mode="bandit")
        assert e.value.code == "EXPERIMENT_BANDIT_DOMAIN_FORBIDDEN"
    # fixed allocation never gated
    check_bandit_gate(domain="talent_flow", risk_class="high", allocation_mode="fixed")


def test_no_employment_promotion_target_exists():
    """§2.1 structural exclusion: no offer/hire/reject target type."""
    for banned in ("offer", "hire", "reject", "employment", "talent"):
        assert not any(banned in t for t in PROMOTION_TARGET_TYPES), banned


# ── State machine (ADR-017 §5) ──────────────────────────────────────


def test_transition_matrix_is_total_over_statuses():
    assert set(_ALLOWED) == set(EXPERIMENT_STATUSES)


def test_terminal_statuses_have_no_exits():
    for terminal in ("promoted", "rejected", "archived"):
        assert _ALLOWED[terminal] == frozenset()


def test_every_nonterminal_can_archive():
    for status, targets in _ALLOWED.items():
        if status in ("promoted", "rejected", "archived"):
            continue
        assert "archived" in targets, status


@pytest.mark.parametrize("from_status", sorted(EXPERIMENT_STATUSES))
@pytest.mark.parametrize("to_status", sorted(EXPERIMENT_STATUSES))
def test_full_illegal_transition_matrix(from_status, to_status):
    """Every (from, to) pair either succeeds or raises the typed code —
    exhaustive enumeration, no sampling."""
    svc = ExperimentService(None)
    if to_status in _ALLOWED[from_status]:
        svc.check_transition(from_status, to_status)
    else:
        with pytest.raises(AppError) as e:
            svc.check_transition(from_status, to_status)
        assert e.value.code == "EXPERIMENT_INVALID_TRANSITION"
        assert e.value.status_code == 422


def test_no_reentry_to_running_from_analyzed():
    """extend never re-randomizes: analyzed cannot return to running."""
    assert "running" not in _ALLOWED["analyzed"]
    assert "scheduled" not in _ALLOWED["analyzed"]


# ── Canonical spec hash ─────────────────────────────────────────────


def test_spec_hash_is_key_order_independent():
    a = {"b": 1, "a": {"y": 2, "x": [1, 2]}}
    b = {"a": {"x": [1, 2], "y": 2}, "b": 1}
    assert canonical_spec_hash(a) == canonical_spec_hash(b)


def test_spec_hash_detects_value_change():
    assert canonical_spec_hash({"a": 1}) != canonical_spec_hash({"a": 2})
