"""R206: CrossHair symbolic-execution contracts over the money/logic core.

Unlike Hypothesis (250 random samples), CrossHair drives an SMT solver to
PROVE each post-condition holds for ALL inputs in the domain — or produce a
concrete counterexample. Targets the integer/boolean logic where the solver
is strongest; Decimal-heavy paths are bounded via int proxies.

Run: crosshair check /tmp/crosshair_contracts.py --per_condition_timeout=20
"""
from decimal import Decimal

from app.controlplane.services.billing import _is_leap, _month_len
from app.controlplane.services.rating import compute_internal_cost_minor


def leap_matches_gregorian(year: int) -> bool:
    """
    pre: 1 <= year <= 9999
    post: __return__ == ((year % 4 == 0) and (year % 100 != 0 or year % 400 == 0))
    """
    return _is_leap(year)


def month_len_in_range(year: int, month: int) -> int:
    """Every month is 28-31 days; February is 28 or 29 by the leap rule.
    pre: 1 <= year <= 9999
    pre: 1 <= month <= 12
    post: 28 <= __return__ <= 31
    post: (month != 2) or (__return__ == (29 if _is_leap(year) else 28))
    """
    return _month_len(year, month)


def cost_reversal_antisymmetry(qty: int) -> int:
    """A reversal exactly negates the forward charge (R52[7]) — no min-fee.
    pre: -100000 < qty < 100000
    post: __return__ == 0
    """
    fwd = compute_internal_cost_minor(Decimal(3), Decimal(qty), "USD", None)
    rev = compute_internal_cost_minor(Decimal(3), Decimal(-qty), "USD", None)
    return fwd + rev


def cost_sign_follows_quantity(qty: int) -> bool:
    """Cost sign tracks quantity sign (never a charge on a credit).
    pre: -100000 < qty < 100000
    post: __return__ == True
    """
    c = compute_internal_cost_minor(Decimal(2), Decimal(qty), "USD", None)
    if qty > 0:
        return c >= 0
    if qty < 0:
        return c <= 0
    return c == 0


def min_fee_never_flips_credit(qty: int, fee: int) -> bool:
    """A minimum fee floors a positive charge but never turns a reversal
    (negative qty) into a positive charge.
    pre: -100000 < qty < 0
    pre: 0 < fee < 100000
    post: __return__ == True
    """
    c = compute_internal_cost_minor(Decimal(1), Decimal(qty), "USD", fee)
    return c <= 0
