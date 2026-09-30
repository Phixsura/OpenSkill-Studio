"""Statistical-core tests (ADR-017 exp05). Pure functions, no DB.

Golden values are pinned via EXACT closed forms (Student t at df=1/2, the
defining quadratic of Wilson endpoints, hand-computable pooled-z examples)
and cross-identities (betainc symmetry, ppf∘cdf) — never by re-running the
implementation's own formula. Monte-Carlo checks pin CI coverage.
"""

import math
import random

import pytest

from app.experiments.services.analysis import (
    Z_975,
    analyze_binary,
    analyze_rate,
    bayes_binary,
    bayes_continuous,
    benjamini_hochberg,
    beta_ppf,
    betainc,
    cuped_adjusted_welch,
    msprt_always_valid_p,
    norm_cdf,
    norm_ppf,
    norm_sf,
    obrien_fleming_boundary,
    t_ppf,
    t_sf,
    welch_from_stats,
    welch_from_values,
    wilson_ci,
)

# ── Numeric layer ────────────────────────────────────────────────────


def test_norm_constants():
    assert norm_cdf(0.0) == pytest.approx(0.5)
    assert norm_sf(1.959963984540054) == pytest.approx(0.025, abs=1e-9)
    assert norm_ppf(0.975) == pytest.approx(1.959963984540054, abs=1e-9)
    assert norm_ppf(0.5) == pytest.approx(0.0, abs=1e-12)


def test_norm_ppf_cdf_roundtrip():
    for p in (0.001, 0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99, 0.999):
        assert norm_cdf(norm_ppf(p)) == pytest.approx(p, abs=1e-10)


def test_betainc_symmetry_identity():
    for a, b, x in ((2.0, 3.0, 0.3), (0.5, 0.5, 0.7), (5.0, 1.5, 0.42)):
        assert betainc(a, b, x) + betainc(b, a, 1.0 - x) == pytest.approx(1.0, abs=1e-10)


def test_betainc_uniform_case():
    # I_x(1,1) is the uniform CDF: exactly x
    for x in (0.1, 0.25, 0.5, 0.9):
        assert betainc(1.0, 1.0, x) == pytest.approx(x, abs=1e-12)


def test_t_sf_exact_closed_forms():
    # df=1 (Cauchy): P(T>t) = 1/2 - arctan(t)/pi
    for t in (0.5, 1.0, 2.0, 5.0):
        assert t_sf(t, 1) == pytest.approx(0.5 - math.atan(t) / math.pi, abs=1e-10)
    # df=2: P(T>t) = 1/2 * (1 - t/sqrt(2+t^2))
    for t in (0.5, 1.0, 3.0):
        assert t_sf(t, 2) == pytest.approx(0.5 * (1 - t / math.sqrt(2 + t * t)), abs=1e-10)


def test_t_sf_converges_to_normal():
    assert t_sf(1.96, 100000) == pytest.approx(norm_sf(1.96), abs=1e-4)


def test_t_ppf_roundtrip():
    for df in (3, 10, 30):
        for p in (0.9, 0.95, 0.975):
            t = t_ppf(p, df)
            assert 1.0 - t_sf(t, df) == pytest.approx(p, abs=1e-6)


def test_beta_ppf_roundtrip():
    for a, b in ((2.0, 5.0), (10.0, 10.0)):
        for p in (0.025, 0.5, 0.975):
            x = beta_ppf(p, a, b)
            assert betainc(a, b, x) == pytest.approx(p, abs=1e-8)


# ── Wilson / binary ──────────────────────────────────────────────────


def test_wilson_endpoints_satisfy_defining_quadratic():
    """Both Wilson endpoints c satisfy (phat - c)^2 = z^2 c(1-c)/n exactly —
    the property that DEFINES the interval, independent of our algebra."""
    for s, n in ((8, 10), (1, 30), (250, 500)):
        phat = s / n
        for c in wilson_ci(s, n):
            if c in (0.0, 1.0):
                continue
            assert (phat - c) ** 2 == pytest.approx(
                Z_975**2 * c * (1 - c) / n, rel=1e-9
            )


def test_wilson_zero_n():
    assert wilson_ci(0, 0) == (0.0, 1.0)


def test_two_proportion_golden_hand_computed():
    """x1=40/100 vs x2=60/100: pooled p=0.5, se=sqrt(0.25*0.02)=0.0707107,
    z = 0.2/0.0707107 = 2.828427, p = 2*Phi(-2.828427) = 0.0046777."""
    r = analyze_binary(40, 100, 60, 100)
    assert r["effect"] == pytest.approx(0.2)
    assert r["relative"] == pytest.approx(0.5)
    assert r["z"] == pytest.approx(2.8284271, abs=1e-6)
    assert r["p"] == pytest.approx(0.0046777, abs=1e-6)
    lo, hi = r["ci"]
    assert lo < 0.2 < hi
    assert lo > 0.0  # significant at 95%


def test_binary_insufficient_data():
    assert analyze_binary(0, 0, 5, 10) == {"insufficient_data": True}


def test_binary_ci_coverage_monte_carlo():
    """Newcombe diff CI: empirical coverage of the true difference must be
    near 95% (loose gate 92-98%) — a wrong sign/width mutant dies here."""
    rng = random.Random(42)
    p1, p2, n = 0.30, 0.40, 400
    covered = 0
    trials = 400
    for _ in range(trials):
        x1 = sum(rng.random() < p1 for _ in range(n))
        x2 = sum(rng.random() < p2 for _ in range(n))
        lo, hi = analyze_binary(x1, n, x2, n)["ci"]
        covered += lo <= (p2 - p1) <= hi
    assert 0.92 <= covered / trials <= 0.995, covered / trials


# ── Welch ────────────────────────────────────────────────────────────


def test_welch_golden_tiny_dataset():
    """{0,2} vs {1,3}: means 1,2; var 2,2; se=sqrt(2); t=1/sqrt(2); df=2;
    p = 2*t_sf(0.70711, 2) = 1 - 0.70711/sqrt(2.5) = 0.55279."""
    r = welch_from_stats(2, 2, 4, 2, 4, 10)
    assert r["effect"] == pytest.approx(1.0)
    assert r["t"] == pytest.approx(1 / math.sqrt(2), abs=1e-9)
    assert r["df"] == pytest.approx(2.0, abs=1e-9)
    assert r["p"] == pytest.approx(1 - (1 / math.sqrt(2)) / math.sqrt(2.5), abs=1e-9)


def test_welch_from_values_matches_stats_path():
    a, b = [1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0]
    r1 = welch_from_values(a, b)
    r2 = welch_from_stats(4, 10, 30, 3, 12, 56)
    assert r1["t"] == pytest.approx(r2["t"])
    assert r1["df"] == pytest.approx(r2["df"])


def test_welch_insufficient():
    assert welch_from_stats(1, 5, 25, 10, 50, 260)["insufficient_data"] is True


# ── Rate (delta method) ──────────────────────────────────────────────


def test_rate_golden():
    """100 events/1000h vs 150/1000h: rates .1/.15, var = 100/1e6+150/1e6 =
    2.5e-4, se=0.0158114, z=0.05/0.0158114=3.1623."""
    r = analyze_rate(100, 1000, 150, 1000)
    assert r["effect"] == pytest.approx(0.05)
    assert r["z"] == pytest.approx(3.16228, abs=1e-4)
    assert r["ci"][0] == pytest.approx(0.05 - Z_975 * 0.015811388, abs=1e-8)


# ── CUPED ────────────────────────────────────────────────────────────


def _arm_stats(xs: list[float], ys: list[float]) -> dict:
    return {
        "n": len(ys), "sum": sum(ys), "sum_sq": sum(y * y for y in ys),
        "cov_sum": sum(xs), "cov_sum_sq": sum(x * x for x in xs),
        "cov_xy_sum": sum(x * y for x, y in zip(xs, ys, strict=True)),
    }


def test_cuped_perfect_covariate_kills_variance():
    """Y = X exactly → theta = 1 and adjusted variance ~0."""
    xc = [1.0, 2.0, 3.0, 4.0, 5.0]
    xt = [1.5, 2.5, 3.5, 4.5, 5.5]
    r = cuped_adjusted_welch(_arm_stats(xc, xc), _arm_stats(xt, xt))
    assert r["theta"] == pytest.approx(1.0, abs=1e-9)
    assert r["variance_reduction_pct"] == pytest.approx(100.0, abs=1e-6)


def test_cuped_uncorrelated_covariate_no_gain():
    rng = random.Random(7)
    yc = [rng.gauss(10, 2) for _ in range(200)]
    yt = [rng.gauss(11, 2) for _ in range(200)]
    xc = [rng.gauss(0, 1) for _ in range(200)]
    xt = [rng.gauss(0, 1) for _ in range(200)]
    r = cuped_adjusted_welch(_arm_stats(xc, yc), _arm_stats(xt, yt))
    assert abs(r["theta"]) < 0.3
    assert r["variance_reduction_pct"] < 10.0


def test_cuped_missing_covariate_returns_none():
    arm = {"n": 10, "sum": 5.0, "sum_sq": 4.0,
           "cov_sum": None, "cov_sum_sq": None, "cov_xy_sum": None}
    assert cuped_adjusted_welch(arm, arm) is None


def test_cuped_preserves_true_effect():
    """Variance shrinks; the effect estimate stays unbiased (X balanced)."""
    rng = random.Random(11)
    xc = [rng.gauss(0, 1) for _ in range(500)]
    xt = [rng.gauss(0, 1) for _ in range(500)]
    yc = [3.0 + 2.0 * x + rng.gauss(0, 0.5) for x in xc]
    yt = [3.5 + 2.0 * x + rng.gauss(0, 0.5) for x in xt]
    r = cuped_adjusted_welch(_arm_stats(xc, yc), _arm_stats(xt, yt))
    assert r["theta"] == pytest.approx(2.0, abs=0.15)
    assert r["effect"] == pytest.approx(0.5, abs=0.15)
    assert r["variance_reduction_pct"] > 80.0


# ── Sequential ───────────────────────────────────────────────────────


def test_msprt_properties():
    assert msprt_always_valid_p(0.0) == 1.0
    p2, p4 = msprt_always_valid_p(2.0), msprt_always_valid_p(4.0)
    assert p4 < p2 < 1.0
    # Exact closed form at z=2, tau=1: p = sqrt(2)*exp(-1)
    assert p2 == pytest.approx(math.sqrt(2.0) * math.exp(-1.0), abs=1e-12)
    with pytest.raises(ValueError):
        msprt_always_valid_p(1.0, tau=0)


def test_obrien_fleming_boundary_shape():
    final = obrien_fleming_boundary(4, 4)
    assert final == pytest.approx(Z_975, abs=1e-9)
    assert obrien_fleming_boundary(1, 4) == pytest.approx(Z_975 * 2.0, abs=1e-9)
    assert obrien_fleming_boundary(2, 4) > obrien_fleming_boundary(3, 4) > final
    with pytest.raises(ValueError):
        obrien_fleming_boundary(5, 4)


# ── Benjamini-Hochberg ───────────────────────────────────────────────


def test_bh_textbook_examples():
    # Largest k with p_(k) <= k/m*q decides; everything ranked below passes
    r = benjamini_hochberg({"a": 0.005, "b": 0.01, "c": 0.03, "d": 0.04}, q=0.05)
    assert r == {"a": True, "b": True, "c": True, "d": True}
    r = benjamini_hochberg({"a": 0.01, "b": 0.2, "c": 0.04}, q=0.05)
    assert r == {"a": True, "b": False, "c": False}
    assert benjamini_hochberg({}) == {}


def test_bh_step_up_rescues_lower_ranks():
    # p=(0.04, 0.049): k=2 passes (0.049 <= 0.05) so k=1 passes too even
    # though 0.04 > 0.025 — the step-up property a naive per-rank mutant loses
    r = benjamini_hochberg({"a": 0.04, "b": 0.049}, q=0.05)
    assert r == {"a": True, "b": True}


# ── Bayesian ─────────────────────────────────────────────────────────


def test_bayes_binary_symmetry_is_half():
    r = bayes_binary(50, 100, 50, 100)
    assert r["p_beat_control"] == pytest.approx(0.5, abs=1e-3)
    assert r["effect"] == pytest.approx(0.0, abs=1e-12)


def test_bayes_binary_matches_normal_approx_large_n():
    r = bayes_binary(400, 1000, 460, 1000)
    p1, p2 = 0.4008, 0.4596  # posterior means with (1,1) prior ≈ raw
    se = math.sqrt(p1 * (1 - p1) / 1000 + p2 * (1 - p2) / 1000)
    approx = norm_cdf((p2 - p1) / se)
    assert r["p_beat_control"] == pytest.approx(approx, abs=0.01)
    assert r["credible_interval"][0] < r["effect"] < r["credible_interval"][1]


def test_bayes_binary_expected_loss_zero_when_clearly_winning():
    r = bayes_binary(300, 1000, 500, 1000)
    assert r["p_beat_control"] > 0.999
    assert r["expected_loss"] < 1e-4


def test_bayes_continuous_directions():
    r = bayes_continuous(100, 1000, 10500, 100, 1100, 12500)
    assert r["p_beat_control"] > 0.5
    flipped = bayes_continuous(100, 1100, 12500, 100, 1000, 10500)
    assert flipped["p_beat_control"] == pytest.approx(1 - r["p_beat_control"], abs=1e-9)
