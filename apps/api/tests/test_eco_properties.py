"""Round-8 property-based & adversarial-fuzz tests (ADR-016 §18).

Hypothesis properties over the statistics kernel (the numbers rankings and
rollout gates are built on) and byte-level fuzzing of every source adapter
(untrusted input must NEVER crash — only parse safely or raise the bounded
security errors). Matches the repo's mutation-testing quality culture.
"""

import json
import math

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.ecosystem.security import EcoSecurityError, sanitize_text
from app.ecosystem.services.adapters import ADAPTERS
from app.ecosystem.services.stats import (
    bradley_terry,
    cohen_kappa,
    linear_trend,
    mean_ci95,
    pairwise_wins_from_scores,
    two_proportion_z_test,
    version_in_range,
    weighted_mean,
    welch_t_test,
)

_FAST = settings(max_examples=60, suppress_health_check=[HealthCheck.too_slow], deadline=None)

finite_floats = st.floats(
    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
)


# ── Statistics kernel properties ────────────────────────────────────


@_FAST
@given(st.lists(finite_floats, min_size=2, max_size=40))
def test_mean_ci95_contains_mean_and_is_ordered(values):
    out = mean_ci95(values)
    assert out["ci95"][0] <= out["mean"] <= out["ci95"][1]
    assert out["n"] == len(values)
    assert out["std"] >= 0


@_FAST
@given(st.lists(st.tuples(finite_floats, st.floats(min_value=0.01, max_value=100)), min_size=1, max_size=30))
def test_weighted_mean_bounded_by_extremes(pairs):
    out = weighted_mean(pairs)
    lo = min(v for v, _ in pairs)
    hi = max(v for v, _ in pairs)
    assert lo - 1e-9 <= out <= hi + 1e-9


@_FAST
@given(st.lists(finite_floats, min_size=2, max_size=30), st.lists(finite_floats, min_size=2, max_size=30))
def test_welch_p_value_in_unit_interval_and_symmetric(a, b):
    p_ab = welch_t_test(a, b)["p_value"]
    p_ba = welch_t_test(b, a)["p_value"]
    assert 0.0 <= p_ab <= 1.0
    assert math.isclose(p_ab, p_ba, abs_tol=1e-9)  # two-sided → symmetric


@_FAST
@given(
    st.integers(min_value=0, max_value=200), st.integers(min_value=1, max_value=200),
    st.integers(min_value=0, max_value=200), st.integers(min_value=1, max_value=200),
)
def test_two_proportion_p_in_unit_interval(sa, na, sb, nb):
    sa, sb = min(sa, na), min(sb, nb)
    out = two_proportion_z_test(sa, na, sb, nb)
    assert 0.0 <= out["p_value"] <= 1.0


@_FAST
@given(
    st.dictionaries(
        st.tuples(
            st.sampled_from(["A", "B", "C", "D"]), st.sampled_from(["A", "B", "C", "D"])
        ).filter(lambda pair: pair[0] != pair[1]),
        st.floats(min_value=0.0, max_value=50.0, allow_nan=False),
        min_size=1,
        max_size=12,
    )
)
def test_bradley_terry_finite_and_complete(wins):
    elo = bradley_terry(wins)
    items = {i for pair in wins for i in pair}
    assert set(elo) == items
    assert all(math.isfinite(v) for v in elo.values())


def test_bradley_terry_dominance_property():
    # If A beats everyone and loses nothing, A must rank first
    wins = {("A", "B"): 5.0, ("A", "C"): 5.0, ("B", "C"): 3.0, ("C", "B"): 2.0}
    elo = bradley_terry(wins)
    assert elo["A"] == max(elo.values())


@_FAST
@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "context": st.sampled_from(["c1", "c2", "c3"]),
                "judge": st.sampled_from(["r1", "r2", "r3"]),
                "item": st.sampled_from(["x", "y", "z"]),
                "score": st.floats(min_value=0, max_value=5, allow_nan=False),
            }
        ),
        max_size=40,
    )
)
def test_pairwise_wins_conservation(rows):
    """Total win mass equals the number of comparisons (each pair contributes
    exactly 1.0 across both directions, ties included)."""
    wins = pairwise_wins_from_scores(rows)
    groups: dict = {}
    for row in rows:
        groups.setdefault((row["context"], row["judge"]), set()).add(row["item"])
    # Count unordered item pairs, honoring duplicates collapsing per group set
    expected = 0
    for (context, judge), _ in groups.items():
        members = [r for r in rows if (r["context"], r["judge"]) == (context, judge)]
        n = len(members)
        expected += sum(
            1
            for i in range(n)
            for j in range(i + 1, n)
            if members[i]["item"] != members[j]["item"]
        )
    assert math.isclose(sum(wins.values()), expected, abs_tol=1e-9)


@_FAST
@given(st.lists(st.floats(min_value=0, max_value=1000, allow_nan=False), min_size=2, max_size=20))
def test_linear_trend_flat_series_projects_constant(values):
    constant = values[0]
    trend = linear_trend([(float(i), constant) for i in range(len(values))])
    assert trend is not None
    assert math.isclose(trend["slope"], 0.0, abs_tol=1e-9)
    assert math.isclose(trend["projected_next"], max(constant, 0.0), abs_tol=0.006)  # impl rounds to 2dp


@_FAST
@given(st.lists(st.sampled_from(["a", "b", "c"]), min_size=1, max_size=30))
def test_cohen_kappa_self_agreement_is_perfect(labels):
    assert cohen_kappa(labels, list(labels)) == 1.0


@_FAST
@given(
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
)
def test_version_in_range_exact_and_caret_consistency(major, minor, patch):
    version = f"{major}.{minor}.{patch}"
    assert version_in_range(version, f"=={version}") is True
    assert version_in_range(version, version) is True
    # ^X.Y.Z always contains itself; never contains the next major
    assert version_in_range(version, f"^{version}") is True
    assert version_in_range(f"{major + 1}.0.0", f"^{version}") is False
    # >= lower bound is reflexive; < is irreflexive
    assert version_in_range(version, f">={version}") is True
    assert version_in_range(version, f"<{version}") is False


# ── Adapter fuzzing: hostile bytes never crash ──────────────────────

_ALLOWED = (EcoSecurityError,)


@_FAST
@given(st.binary(max_size=4096))
def test_all_adapters_survive_arbitrary_bytes(raw):
    for adapter in ADAPTERS.values():
        try:
            items = adapter.parse(raw, {})
        except _ALLOWED:
            continue  # bounded security error is the ONLY allowed exception
        assert isinstance(items, list)


@_FAST
@given(st.recursive(
    st.none() | st.booleans() | st.integers(min_value=-10**6, max_value=10**6)
    | st.floats(allow_nan=False, allow_infinity=False, width=32)
    | st.text(max_size=50),
    lambda children: st.lists(children, max_size=5)
    | st.dictionaries(st.text(max_size=15), children, max_size=5),
    max_leaves=25,
))
def test_all_adapters_survive_arbitrary_json(doc):
    raw = json.dumps(doc).encode()
    for adapter in ADAPTERS.values():
        try:
            items = adapter.parse(raw, {})
        except _ALLOWED:
            continue
        assert isinstance(items, list)
        for item in items:
            # Every produced observation candidate is storage-safe:
            # a stable 64-hex hash and NUL-free normalized payload
            assert len(item.raw_hash) == 64
            flat = json.dumps(item.normalized, default=str)
            assert "\\u0000" not in flat and "\x00" not in flat


@_FAST
@given(st.text(max_size=300))
def test_sanitize_text_idempotent_and_control_free(text):
    once = sanitize_text(text, 200)
    if once is None:
        return
    assert sanitize_text(once, 200) == once  # idempotent
    assert not any(ord(c) < 32 and c not in "\t\n\r" for c in once)
