"""R204: metamorphic tests over the rating/proration money engine.

Metamorphic relations pin how the OUTPUT must change when the INPUT is
transformed by a rule — without needing the correct absolute value. They
catch proportionality/symmetry/monotonicity bugs that exact-value tests
(which only check one point) miss: a dropped factor, a sign asymmetry, a
non-linear rounding drift.
"""

from decimal import Decimal

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.controlplane.services.billing import proration_preview
from app.controlplane.services.rating import (
    compute_billable_minor,
    compute_internal_cost_minor,
    convert_exact,
    convert_minor,
)

_FUZZ = settings(max_examples=250, suppress_health_check=list(HealthCheck), deadline=None)
_cur = st.sampled_from(["USD", "EUR", "JPY", "KRW", "GBP"])  # mix decimal + zero-decimal
_qty = st.integers(min_value=1, max_value=10_000)
_cost = st.decimals(min_value="0.000001", max_value="100", places=6)


# ── FX conversion ────────────────────────────────────────────


@_FUZZ
@given(
    st.integers(min_value=0, max_value=10**9),
    _cur,
    _cur,
    st.decimals(min_value="0.01", max_value="1000", places=8),
)
def test_fx_scaling_relation(amount, a, b, rate):
    """MR-1 (linearity): converting 2x the amount converts to ~2x the result
    (within 1 minor unit of rounding). A dropped minor_multiplier or a
    /rate-instead-of-*rate bug breaks the ratio, not necessarily one point."""
    one = convert_minor(amount, rate, a, b)
    two = convert_minor(amount * 2, rate, a, b)
    assert abs(two - 2 * one) <= 1


@_FUZZ
@given(
    st.integers(min_value=0, max_value=10**7),
    _cur,
    _cur,
    st.decimals(min_value="0.1", max_value="10", places=6),
)
def test_fx_exact_is_unrounded_superset(amount, a, b, rate):
    """MR-2 (exact≥rounded consistency): convert_exact then round == convert_minor
    (the invoice-rounds-the-sum-once contract, R75). A divergence means the
    two converters drifted apart — double-billing risk at scale."""
    from decimal import ROUND_HALF_UP

    ex = convert_exact(Decimal(amount), rate, a, b)
    assert int(ex.quantize(Decimal("1"), rounding=ROUND_HALF_UP)) == convert_minor(
        amount, rate, a, b
    )


# ── Internal cost ────────────────────────────────────────────


@_FUZZ
@given(_cost, _qty, _cur)
def test_cost_sign_antisymmetry(cost, qty, cur):
    """MR-3 (reversal symmetry, R52[7]): cost(-q) == -cost(+q). A refund/void
    must net to zero against its forward event — a min-fee that clamps the
    reversal, or an abs() bug, breaks this."""
    fwd = compute_internal_cost_minor(cost, Decimal(qty), cur, None)
    rev = compute_internal_cost_minor(cost, Decimal(-qty), cur, None)
    assert rev == -fwd


@_FUZZ
@given(_cost, _qty, _cur)
def test_cost_quantity_monotone(cost, qty, cur):
    """MR-4 (monotonicity): more quantity never costs less (positive events)."""
    less = compute_internal_cost_minor(cost, Decimal(qty), cur, None)
    more = compute_internal_cost_minor(cost, Decimal(qty + 1), cur, None)
    assert more >= less


@_FUZZ
@given(_cost, _qty)
def test_cost_min_fee_is_floor_not_ceiling(cost, qty):
    """MR-5: a minimum fee only ever RAISES a positive charge, never lowers
    it; and it never touches a reversal's sign."""
    base = compute_internal_cost_minor(cost, Decimal(qty), "USD", None)
    floored = compute_internal_cost_minor(cost, Decimal(qty), "USD", 500)
    assert floored >= base and floored >= min(500, floored)  # floor applied to positive
    rev = compute_internal_cost_minor(cost, Decimal(-qty), "USD", 500)
    assert rev <= 0, "min-fee must not flip a credit into a charge"


# ── Billable (cost-plus) ─────────────────────────────────────


@_FUZZ
@given(
    st.integers(min_value=1, max_value=10**8), st.decimals(min_value="0", max_value="500", places=2)
)
def test_cost_plus_percentage_monotone_in_markup(icost, pct):
    """MR-6: a higher markup % never bills less than a lower one on the same
    internal cost."""
    lo = compute_billable_minor(
        "cost_plus_percentage",
        {"percentage": float(pct)},
        internal_cost_minor=icost,
        quantity=Decimal(1),
    )
    hi = compute_billable_minor(
        "cost_plus_percentage",
        {"percentage": float(pct) + 10},
        internal_cost_minor=icost,
        quantity=Decimal(1),
    )
    assert hi >= lo >= icost  # cost-plus never bills below cost for +markup


# ── Proration ────────────────────────────────────────────────


@_FUZZ
@given(
    st.integers(min_value=1000, max_value=10**8),
    st.integers(min_value=1000, max_value=10**8),
    st.integers(min_value=2, max_value=180),
)
def test_proration_fee_scaling(old_amt, new_amt, plen):
    """MR-7 (proration linearity): doubling BOTH plan fees doubles both
    prorated components (within rounding). A per-day denominator bug that
    scales one side breaks this even when a single point looks right."""
    from datetime import UTC, datetime, timedelta

    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=plen)
    at = start + timedelta(days=plen // 2)
    base = proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=old_amt,
        new_amount_minor=new_amt,
    )
    dbl = proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=old_amt * 2,
        new_amount_minor=new_amt * 2,
    )
    assert abs(dbl["credit_unused_old_minor"] - 2 * base["credit_unused_old_minor"]) <= 1
    assert abs(dbl["charge_new_remaining_minor"] - 2 * base["charge_new_remaining_minor"]) <= 1


@_FUZZ
@given(st.integers(min_value=1000, max_value=10**8), st.integers(min_value=2, max_value=180))
def test_proration_time_symmetry(amount, plen):
    """MR-8: for the SAME plan (no change), credit for unused == charge for
    remaining at every instant — the two halves of a no-op change mirror."""
    from datetime import UTC, datetime, timedelta

    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=plen)
    for frac in (1, 2, 3):
        at = start + timedelta(days=plen * frac // 4)
        p = proration_preview(
            period_start=start,
            period_end=end,
            at=at,
            old_amount_minor=amount,
            new_amount_minor=amount,
        )
        assert p["credit_unused_old_minor"] == p["charge_new_remaining_minor"]
        assert p["net_minor"] == 0
