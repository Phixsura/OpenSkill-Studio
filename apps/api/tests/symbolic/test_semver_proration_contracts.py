"""R206b: CrossHair contracts — semver total-order + proration conservation.
Run: crosshair check /tmp/crosshair_contracts2.py --per_condition_timeout=20
"""

from datetime import UTC, datetime, timedelta

from app.controlplane.services.billing import proration_preview
from app.services.workflow_pack import _parse_semver


def semver_patch_monotone(a: int, b: int) -> bool:
    """Within one X.Y line, a higher patch sorts strictly higher.
    pre: 0 <= a <= 999
    pre: 0 <= b <= 999
    pre: a < b
    post: __return__ == True
    """
    return _parse_semver(f"1.2.{a}") < _parse_semver(f"1.2.{b}")


def semver_release_beats_prerelease(patch: int) -> bool:
    """A release ranks above its own prerelease (semver §11).
    pre: 0 <= patch <= 999
    post: __return__ == True
    """
    return _parse_semver(f"1.0.{patch}") > _parse_semver(f"1.0.{patch}-rc.1")


def semver_total_and_reflexive(x: int) -> bool:
    """Parsing is deterministic: equal strings → equal keys.
    pre: 0 <= x <= 9999
    post: __return__ == True
    """
    return _parse_semver(f"3.1.{x}") == _parse_semver(f"3.1.{x}")


def proration_net_is_component_sum(old_amt: int, new_amt: int, offset: int) -> bool:
    """net == charge_new − credit_old + seat_proration, ALWAYS (no seats here).
    pre: 0 <= old_amt <= 10**7
    pre: 0 <= new_amt <= 10**7
    pre: 0 <= offset <= 30
    post: __return__ == True
    """
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=30)
    at = start + timedelta(days=offset)
    p = proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=old_amt,
        new_amount_minor=new_amt,
    )
    return p["net_minor"] == (
        p["charge_new_remaining_minor"] - p["credit_unused_old_minor"] + p["seat_proration_minor"]
    )


def proration_days_left_bounded(offset: int) -> bool:
    """days_left is always within [0, total_days] — even for out-of-range at.
    pre: -50 <= offset <= 80
    post: __return__ == True
    """
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=30)
    at = start + timedelta(days=offset)
    p = proration_preview(
        period_start=start, period_end=end, at=at, old_amount_minor=1000, new_amount_minor=2000
    )
    return 0 <= p["days_left"] <= p["total_days"]
