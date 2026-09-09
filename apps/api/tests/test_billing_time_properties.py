"""R195: clock-edge + property sweep over the PURE billing time/proration
functions (industry technique: billing-engine clock testing, cf. Stripe test
clocks). No DB, no frozen clock needed — the functions take explicit
datetimes, so Hypothesis drives the calendar directly."""

from datetime import UTC, datetime, timedelta

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.controlplane.services.billing import _add_interval, proration_preview

_FUZZ = settings(max_examples=300, suppress_health_check=list(HealthCheck), deadline=None)

_dt = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2032, 12, 31),
    timezones=st.just(UTC),
)
_money = st.integers(min_value=0, max_value=10**10)
_seats = st.integers(min_value=0, max_value=10**4)


@_FUZZ
@given(_dt, st.sampled_from(["month", "year"]))
def test_add_interval_total_and_advancing(start, interval):
    end = _add_interval(start, interval)
    assert end > start
    # Chaining 24 intervals never raises (leap/month-end clamps hold).
    cur = start
    for _ in range(24):
        cur = _add_interval(cur, interval)
    assert cur > start


def test_add_interval_calendar_edges():
    # Leap-day anniversary: Feb 29 → Feb 28 (non-leap) → stays valid.
    d = _add_interval(datetime(2024, 2, 29, tzinfo=UTC), "year")
    assert (d.month, d.day) == (2, 28)
    # Month-end clamp: Jan 31 → Feb 29 (leap 2024).
    d = _add_interval(datetime(2024, 1, 31, tzinfo=UTC), "month")
    assert (d.month, d.day) == (2, 29)
    # Dec 31 → Jan 31 (year rollover keeps the day).
    d = _add_interval(datetime(2025, 12, 31, tzinfo=UTC), "month")
    assert (d.year, d.month, d.day) == (2026, 1, 31)


@_FUZZ
@given(_dt, st.integers(min_value=1, max_value=400), st.integers(min_value=-5, max_value=450),
       _money, _money, _seats, _seats, _money)
def test_proration_total_and_bounded(start, plen, at_off, old_amt, new_amt, old_seats, new_seats, seat_price):
    end = start + timedelta(days=plen)
    at = start + timedelta(days=at_off)  # may fall before/after the period
    p = proration_preview(
        period_start=start, period_end=end, at=at,
        old_amount_minor=old_amt, new_amount_minor=new_amt,
        old_seats=old_seats, new_seats=new_seats, seat_price_minor=seat_price,
    )
    assert 0 <= p["days_left"] <= p["total_days"]
    assert p["credit_unused_old_minor"] >= 0
    assert p["charge_new_remaining_minor"] >= 0
    # denom == period length here → prorated parts never exceed the full fee
    # (+1 tolerance for ROUND_HALF_UP).
    assert p["credit_unused_old_minor"] <= old_amt + 1
    assert p["charge_new_remaining_minor"] <= new_amt + 1
    assert p["net_minor"] == (
        p["charge_new_remaining_minor"] - p["credit_unused_old_minor"] + p["seat_proration_minor"]
    )


@_FUZZ
@given(_dt, st.integers(min_value=1, max_value=400), _money, _seats, _money)
def test_proration_identity_change_is_free(start, plen, amt, seats, seat_price):
    """Same plan, same seats → net 0 at ANY change instant (incl. edges)."""
    end = start + timedelta(days=plen)
    for at in (start, start + timedelta(days=plen // 2), end):
        p = proration_preview(
            period_start=start, period_end=end, at=at,
            old_amount_minor=amt, new_amount_minor=amt,
            old_seats=seats, new_seats=seats, seat_price_minor=seat_price,
        )
        assert p["net_minor"] == 0


@_FUZZ
@given(_dt, st.integers(min_value=2, max_value=400), _money, _money)
def test_proration_monotone_in_time(start, plen, old_amt, new_amt):
    """Later change instant → less unused-old credit and less new-plan charge."""
    end = start + timedelta(days=plen)
    early = proration_preview(period_start=start, period_end=end, at=start,
                              old_amount_minor=old_amt, new_amount_minor=new_amt)
    late = proration_preview(period_start=start, period_end=end, at=end,
                             old_amount_minor=old_amt, new_amount_minor=new_amt)
    assert late["credit_unused_old_minor"] <= early["credit_unused_old_minor"]
    assert late["charge_new_remaining_minor"] <= early["charge_new_remaining_minor"]
    assert late["days_left"] == 0 and late["credit_unused_old_minor"] == 0
