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


# ── R202 (AST-mutation survivors): pin the exact math the property sweep
# missed. Each assertion below kills specific surviving mutants. ──


def test_leap_rule_century_boundaries():
    """Kills _is_leap survivors (÷100/÷400 flips + Eq→NotEq): the Gregorian
    century rule — 2100 is NOT leap (÷100), 2000/2400 ARE (÷400)."""
    from app.controlplane.services.billing import _is_leap

    assert _is_leap(2024) and _is_leap(2000) and _is_leap(2400)
    assert not _is_leap(2100) and not _is_leap(2200) and not _is_leap(1900)
    assert not _is_leap(2023) and not _is_leap(2025)


def test_month_len_exact_table():
    """Kills the L65 month-table survivors (31→32 etc.): every month's exact
    length, both leap and non-leap."""
    from app.controlplane.services.billing import _month_len

    assert [_month_len(2023, m) for m in range(1, 13)] == [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    assert [_month_len(2024, m) for m in range(1, 13)] == [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def test_add_interval_exact_dates():
    """Kills the year-path survivors (start.year+1→+2 etc. escaped the
    ordering-only properties): exact output dates."""
    from datetime import UTC, datetime

    from app.controlplane.services.billing import _add_interval

    assert _add_interval(datetime(2025, 3, 15, tzinfo=UTC), "year") == datetime(2026, 3, 15, tzinfo=UTC)
    assert _add_interval(datetime(2025, 3, 15, tzinfo=UTC), "month") == datetime(2025, 4, 15, tzinfo=UTC)
    assert _add_interval(datetime(2023, 2, 28, tzinfo=UTC), "year") == datetime(2024, 2, 28, tzinfo=UTC)


def test_proration_exact_numbers():
    """Kills the L126-134 Sub→Add + L149 GtE→Gt survivors: exact minor-unit
    proration on a round case, both signs of net, and the net==0 mode edge."""
    from datetime import UTC, datetime

    from app.controlplane.services.billing import proration_preview

    start, end = datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 1, 31, tzinfo=UTC)
    mid = datetime(2026, 1, 16, tzinfo=UTC)  # 15/30 days used
    p = proration_preview(period_start=start, period_end=end, at=mid,
                          old_amount_minor=3000, new_amount_minor=6000)
    assert p["total_days"] == 30 and p["days_left"] == 15
    assert p["credit_unused_old_minor"] == 1500   # 3000/30*15
    assert p["charge_new_remaining_minor"] == 3000  # 6000/30*15
    assert p["net_minor"] == 1500 and p["mode"] == "immediate"

    down = proration_preview(period_start=start, period_end=end, at=mid,
                             old_amount_minor=6000, new_amount_minor=3000)
    assert down["net_minor"] == -1500 and down["mode"] == "next_period_default"

    # net == 0 must be "immediate" (>= not >) — kills L149 GtE→Gt
    same = proration_preview(period_start=start, period_end=end, at=mid,
                             old_amount_minor=3000, new_amount_minor=3000)
    assert same["net_minor"] == 0 and same["mode"] == "immediate"


def test_proration_seat_band_exact():
    """Kills the seat-band survivors (band/covered/correct arith): exact
    seat component under included-seat changes and a mid-period decrease."""
    from datetime import UTC, datetime

    from app.controlplane.services.billing import proration_preview

    start, end = datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 1, 31, tzinfo=UTC)
    mid = datetime(2026, 1, 16, tzinfo=UTC)
    # 10 billable seats; old plan includes 2, new includes 5, price 100/seat.
    # covered = (10-2)*100 = 800; correct = (max(10,10)-5)*100 = 500
    # seat component = (500-800)/30 * 15 = -150
    p = proration_preview(
        period_start=start, period_end=end, at=mid,
        old_amount_minor=0, new_amount_minor=0,
        old_seats=10, new_seats=10, seat_price_minor=100,
        billable_seats=10, old_included_seats=2, new_included_seats=5,
    )
    assert p["seat_proration_minor"] == -150, p

    # Mid-period seat DECREASE: band = max(billable, old_seats) keeps the
    # floor — new_seats=4 below band 10 must NOT produce a refund beyond the
    # included-seat delta (band holds at 10).
    q = proration_preview(
        period_start=start, period_end=end, at=mid,
        old_amount_minor=0, new_amount_minor=0,
        old_seats=10, new_seats=4, seat_price_minor=100,
        billable_seats=10, old_included_seats=0, new_included_seats=0,
    )
    # covered = 10*100 = 1000; correct = max(4,10)*100 = 1000 → 0
    assert q["seat_proration_minor"] == 0, q


def test_add_interval_march31_into_leap_year():
    """Kills the L53 month==2/Eq survivors: a March-31 start whose TARGET
    year is leap must keep day 31 (the mutant applies the Feb-29 clamp to
    March and squeezes it to 29)."""
    from datetime import UTC, datetime

    from app.controlplane.services.billing import _add_interval

    assert _add_interval(datetime(2027, 3, 31, tzinfo=UTC), "year") == datetime(2028, 3, 31, tzinfo=UTC)
    assert _add_interval(datetime(2027, 1, 31, tzinfo=UTC), "year") == datetime(2028, 1, 31, tzinfo=UTC)


def test_proration_degenerate_denominators():
    """Kills the L97/L100 floor survivors: a zero-length period clamps
    total_days to 1 (never 0-divide), and an explicit natural_days=0 falls
    back to the same floor."""
    from datetime import UTC, datetime

    from app.controlplane.services.billing import proration_preview

    t = datetime(2026, 5, 1, tzinfo=UTC)
    p = proration_preview(period_start=t, period_end=t, at=t,
                          old_amount_minor=3000, new_amount_minor=3000)
    assert p["total_days"] == 1 and p["days_left"] == 1 - max(min(0, 1), 0)
    assert p["net_minor"] == 0

    # Python-truthiness pin: `natural_days or total_days` collapses an
    # explicit 0 to the period length (0 is falsy) — so natural_days=0
    # behaves exactly like None. This makes the max(...,1)-floor mutant
    # EQUIVALENT (documented, not chased); assert the collapse itself.
    q = proration_preview(period_start=t, period_end=t.replace(day=11), at=t,
                          old_amount_minor=1000, new_amount_minor=2000,
                          natural_days=0)
    assert q["credit_unused_old_minor"] == 1000
    assert q["charge_new_remaining_minor"] == 2000
