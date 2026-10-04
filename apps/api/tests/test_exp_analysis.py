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
    moments_from_stats,
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


# ── Mutation-killer batch (survivor sweep round 1) ───────────────────


def test_t_sf_rejects_zero_df():
    with pytest.raises(ValueError):
        t_sf(1.0, 0)


def test_wilson_clamps_exactly_at_extremes():
    assert wilson_ci(0, 5)[0] == 0.0
    assert wilson_ci(5, 5)[1] == 1.0
    lo, hi = wilson_ci(0, 5)
    assert lo < hi


def test_binary_treatment_side_zero_n_guard():
    assert analyze_binary(5, 10, 0, 0) == {"insufficient_data": True}
    assert analyze_binary(5, 10, 5, 0) == {"insufficient_data": True}


def test_binary_zero_se_and_zero_control_rate():
    # all-success both arms: pooled variance 0 → z defined as 0, p = 1
    r = analyze_binary(10, 10, 10, 10)
    assert r["z"] == 0.0 and r["p"] == pytest.approx(1.0)
    # control rate 0 → relative is None, never a division
    assert analyze_binary(0, 10, 5, 10)["relative"] is None


def test_newcombe_bounds_recomputed_independently():
    """Both Newcombe bounds pinned by explicit reconstruction from Wilson
    pieces — any sign/exponent mutant in the source formula dies here."""
    x1, n1, x2, n2 = 30, 90, 45, 80
    r = analyze_binary(x1, n1, x2, n2)
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson_ci(x1, n1)
    l2, u2 = wilson_ci(x2, n2)
    lo = (p2 - p1) - math.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2)
    hi = (p2 - p1) + math.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2)
    assert r["ci"][0] == pytest.approx(lo, abs=1e-12)
    assert r["ci"][1] == pytest.approx(hi, abs=1e-12)


def test_moments_single_observation():
    assert moments_from_stats(1, 5, 25) == (5.0, 0.0)


def test_welch_treatment_side_insufficient():
    assert welch_from_stats(10, 50, 260, 1, 5, 25)["insufficient_data"] is True


def test_welch_zero_variance_branch_exact():
    # constants: {2,2,2} vs {3,3,3} — vars 0, effect 1, p 0, ci degenerate
    r = welch_from_stats(3, 6, 12, 3, 9, 27)
    assert r["effect"] == pytest.approx(1.0)
    assert r["ci"] == [1.0, 1.0]
    assert r["t"] == 0.0 and r["p"] == 0.0
    assert r["df"] == 4  # n1 + n2 - 2
    assert r["control"]["var"] == pytest.approx(0.0)
    same = welch_from_stats(3, 6, 12, 3, 6, 12)
    assert same["p"] == 1.0 and same["effect"] == 0.0


def test_welch_asymmetric_df_and_ci_pinned():
    """[1..5] vs [10,12,...,28]: v1=2.5, v2=36.667 — hand-derived
    df = 4.16667² / (0.0625 + 1.493827) = 11.1553."""
    r = welch_from_stats(5, 15, 55, 10, 190, 3940)
    assert r["effect"] == pytest.approx(16.0)
    assert r["df"] == pytest.approx(11.1553, abs=1e-3)
    se = math.sqrt(2.5 / 5 + (330 / 9) / 10)
    tcrit = t_ppf(0.975, r["df"])
    assert r["ci"][0] == pytest.approx(16.0 - tcrit * se, abs=1e-6)
    assert r["ci"][1] == pytest.approx(16.0 + tcrit * se, abs=1e-6)


def test_rate_guards_each_side_and_zero_se():
    assert analyze_rate(5, 10, 0, 0) == {"insufficient_data": True}
    assert analyze_rate(0, 0, 5, 10) == {"insufficient_data": True}
    r = analyze_rate(0, 100, 0, 100)
    assert r["z"] == 0.0 and r["p"] == pytest.approx(1.0)
    assert analyze_rate(0, 100, 5, 100)["relative"] is None


def test_rate_ci_upper_bound_pinned():
    r = analyze_rate(100, 1000, 150, 1000)
    se = math.sqrt(100 / 1000**2 + 150 / 1000**2)
    assert r["ci"][1] == pytest.approx(0.05 + Z_975 * se, abs=1e-12)


def test_cuped_guards():
    tiny = _arm_stats([1.0], [2.0])
    big = _arm_stats([1.0, 2.0, 3.0], [2.0, 3.0, 4.0])
    assert cuped_adjusted_welch(tiny, big) is None  # n<=1 arm
    const_x_c = _arm_stats([2.0, 2.0, 2.0], [1.0, 2.0, 3.0])
    const_x_t = _arm_stats([2.0, 2.0, 2.0], [2.0, 3.0, 4.0])
    assert cuped_adjusted_welch(const_x_c, const_x_t) is None  # var(X)=0


def test_cuped_matches_explicit_adjusted_values():
    """The sufficient-stats path must equal welch over the explicitly
    adjusted values Z = Y - theta(X - x̄) — kills any cross-sum mutant."""
    xc = [1.0, 3.0, 5.0, 7.0]
    yc = [2.1, 3.9, 6.2, 7.8]
    xt = [2.0, 4.0, 6.0, 8.0]
    yt = [3.2, 5.1, 6.8, 9.1]
    r = cuped_adjusted_welch(_arm_stats(xc, yc), _arm_stats(xt, yt))
    theta, xbar = r["theta"], (sum(xc) + sum(xt)) / 8.0
    zc = [y - theta * (x - xbar) for x, y in zip(xc, yc, strict=True)]
    zt = [y - theta * (x - xbar) for x, y in zip(xt, yt, strict=True)]
    expected = welch_from_values(zc, zt)
    assert r["effect"] == pytest.approx(expected["effect"], abs=1e-9)
    assert r["t"] == pytest.approx(expected["t"], abs=1e-9)
    assert r["df"] == pytest.approx(expected["df"], abs=1e-9)


def test_cuped_constant_outcome_reports_zero_reduction():
    yc = [5.0, 5.0, 5.0]
    yt = [5.0, 5.0, 5.0]
    r = cuped_adjusted_welch(
        _arm_stats([1.0, 2.0, 3.0], yc), _arm_stats([1.5, 2.5, 3.5], yt)
    )
    assert r is not None
    assert r["variance_reduction_pct"] == 0.0


def test_bh_boundary_equality_passes():
    assert benjamini_hochberg({"a": 0.05}, q=0.05) == {"a": True}


def test_bayes_binary_guards_and_small_n_exact():
    assert bayes_binary(5, 10, 0, 0) == {"insufficient_data": True}
    assert bayes_binary(0, 0, 5, 10) == {"insufficient_data": True}
    # (0/1) vs (1/1) with uniform prior: Beta(1,2) vs Beta(2,1),
    # P(p2 > p1) = ∫ 2x(2x - x²) dx = 4/3 - 1/2 = 5/6
    r = bayes_binary(0, 1, 1, 1)
    assert r["p_beat_control"] == pytest.approx(5.0 / 6.0, abs=1e-3)
    assert r["control"]["posterior_mean"] == pytest.approx(1.0 / 3.0, abs=1e-12)
    assert r["treatment"]["posterior_mean"] == pytest.approx(2.0 / 3.0, abs=1e-12)
    # Beta(2,1) cdf = x² → quantiles are sqrt(p)
    assert r["treatment"]["ci"][0] == pytest.approx(math.sqrt(0.025), abs=1e-6)
    assert r["treatment"]["ci"][1] == pytest.approx(math.sqrt(0.975), abs=1e-6)


def test_bayes_binary_expected_loss_symmetric_pinned():
    """50/100 both arms: diff=0 → EL = se/sqrt(2π) with
    se = sqrt(2·51·51/(102²·103)) — hand-derived closed form."""
    r = bayes_binary(50, 100, 50, 100)
    var = 51.0 * 51.0 / (102.0**2 * 103.0)
    se = math.sqrt(2.0 * var)
    assert r["expected_loss"] == pytest.approx(se / math.sqrt(2 * math.pi), abs=1e-9)


def test_bayes_continuous_zero_variance_branch():
    up = bayes_continuous(3, 6, 12, 3, 9, 27)  # constants 2 vs 3
    assert up["p_beat_control"] == 1.0 and up["expected_loss"] == 0.0
    down = bayes_continuous(3, 9, 27, 3, 6, 12)
    assert down["p_beat_control"] == 0.0
    flat = bayes_continuous(3, 6, 12, 3, 6, 12)
    assert flat["p_beat_control"] == 0.5


def test_bayes_continuous_interval_and_loss_pinned():
    n1, s1, ss1 = 100, 1000, 10500
    n2, s2, ss2 = 100, 1100, 12500
    r = bayes_continuous(n1, s1, ss1, n2, s2, ss2)
    m1, v1 = moments_from_stats(n1, s1, ss1)
    m2, v2 = moments_from_stats(n2, s2, ss2)
    se = math.sqrt(v1 / n1 + v2 / n2)
    diff = m2 - m1
    assert r["credible_interval"][0] == pytest.approx(diff - Z_975 * se, abs=1e-9)
    assert r["credible_interval"][1] == pytest.approx(diff + Z_975 * se, abs=1e-9)
    z0 = diff / se
    el = se * math.exp(-z0 * z0 / 2) / math.sqrt(2 * math.pi) - diff * norm_sf(z0)
    assert r["expected_loss"] == pytest.approx(max(0.0, el), abs=1e-9)


# ── Mutation-killer batch round 2 ────────────────────────────────────
# Surviving mutants documented as equivalent/accuracy-limited:
#   t_sf L127 GtE->Gt (t=0: both branches yield 0.5);
#   cuped L299 Or->And + LtE->Lt (guard redundant with welch's own n>1 guard —
#     both paths return None);
#   bayes L399 range-start 1->2 (drops one of 2001 grid points, ~1e-6);
#   bayes L410/L434 Gt->GtE (se==0 unreachable for beta posteriors / handled
#     identically by the explicit se==0 branch).


def test_t_sf_negative_symmetry():
    for t, df in ((1.0, 5), (2.5, 3), (0.3, 12)):
        assert t_sf(-t, df) + t_sf(t, df) == pytest.approx(1.0, abs=1e-12)


def test_cuped_two_element_arms_allowed():
    r = cuped_adjusted_welch(
        _arm_stats([1.0, 2.0], [2.0, 4.0]), _arm_stats([1.5, 2.5], [3.0, 5.0])
    )
    assert r is not None


def test_cuped_theta_pinned_independently():
    """theta must equal pooled cov(X,Y)/var(X) computed from raw values in
    the test itself — kills any pooled-sum mutant without tautology."""
    xc, yc = [1.0, 3.0, 5.0, 7.0], [2.1, 3.9, 6.2, 7.8]
    xt, yt = [2.0, 4.0, 6.0, 8.0], [3.2, 5.1, 6.8, 9.1]
    xs, ys = xc + xt, yc + yt
    n = len(xs)
    xbar, ybar = sum(xs) / n, sum(ys) / n
    cov = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys, strict=True))
    varx = sum((x - xbar) ** 2 for x in xs)
    expected_theta = cov / varx
    r = cuped_adjusted_welch(_arm_stats(xc, yc), _arm_stats(xt, yt))
    assert r["theta"] == pytest.approx(expected_theta, abs=1e-9)


def test_bayes_binary_expected_loss_asymmetric_pinned():
    """40/100 vs 60/100: EL recomputed in-test from posterior moments —
    kills sign mutants in the normal-approx loss formula."""
    r = bayes_binary(40, 100, 60, 100)
    a1, b1, a2, b2 = 41.0, 61.0, 61.0, 41.0
    m1, m2 = a1 / (a1 + b1), a2 / (a2 + b2)
    v1 = a1 * b1 / ((a1 + b1) ** 2 * (a1 + b1 + 1.0))
    v2 = a2 * b2 / ((a2 + b2) ** 2 * (a2 + b2 + 1.0))
    se = math.sqrt(v1 + v2)
    diff = m2 - m1
    z0 = diff / se
    el = se * math.exp(-z0 * z0 / 2.0) / math.sqrt(2 * math.pi) - diff * norm_sf(z0)
    assert r["expected_loss"] == pytest.approx(max(0.0, el), abs=1e-12)


# ── pool_stratified (v2 batch 8, post-stratification by time) ────────


def test_pool_stratified_inverse_variance_math():
    from app.experiments.services.analysis import pool_stratified

    # two strata, equal se → plain average; tighter stratum dominates
    equal = pool_stratified([(0.10, 0.02), (0.20, 0.02)])
    assert abs(equal["effect"] - 0.15) < 1e-12
    assert equal["strata"] == 2
    skewed = pool_stratified([(0.10, 0.01), (0.20, 0.10)])
    assert abs(skewed["effect"] - 0.10) < 0.005  # tight stratum dominates
    # pooled se is tighter than any single stratum
    assert skewed["se"] < 0.01
    assert 0.0 <= skewed["p"] <= 1.0
    assert skewed["ci"][0] < skewed["effect"] < skewed["ci"][1]


def test_pool_stratified_totality():
    from app.experiments.services.analysis import pool_stratified

    assert pool_stratified([]) is None
    assert pool_stratified([(0.1, 0.02)]) is None  # one stratum = no pooling
    # non-finite / non-positive se strata are dropped, not crashed on
    assert pool_stratified([(0.1, 0.0), (float("inf"), 0.1), (0.2, float("nan"))]) is None
    ok = pool_stratified([(0.1, 0.0), (0.1, 0.02), (0.2, 0.02)])
    assert ok is not None and ok["strata"] == 2


# ── thompson_weights (v2 batch 10, bandit suggestion) ────────────────


def test_thompson_weights_favor_the_better_arm():
    from app.experiments.services.analysis import thompson_weights

    result = thompson_weights({"control": (50, 1000), "treatment": (150, 1000)})
    assert result["p_best"]["treatment"] > 0.99
    assert result["suggested_weights_bp"]["treatment"] > 9900
    assert sum(result["suggested_weights_bp"].values()) == 10_000
    # deterministic: seeded Monte Carlo
    again = thompson_weights({"control": (50, 1000), "treatment": (150, 1000)})
    assert again == result


def test_thompson_weights_uncertain_arms_split():
    from app.experiments.services.analysis import thompson_weights

    result = thompson_weights({"a": (10, 100), "b": (11, 100)})
    assert 0.2 < result["p_best"]["a"] < 0.8
    assert sum(result["suggested_weights_bp"].values()) == 10_000


def test_thompson_weights_totality():
    from app.experiments.services.analysis import thompson_weights

    assert thompson_weights({}) is None
    assert thompson_weights({"only": (5, 10)}) is None
    # zero-n and corrupt arms dropped
    assert thompson_weights({"a": (5, 0), "b": (20, 10)}) is None
    ok = thompson_weights({"a": (5, 0), "b": (2, 10), "c": (8, 10)})
    assert ok is not None and set(ok["p_best"]) == {"b", "c"}


# ── Round-10 mutation killers (analysis cores) ───────────────────────


def test_chi2_sf_pins_in_pure_suite():
    """Mutation-killer copies of the critical-value pins (the holdout suite
    holds the originals, but the fast mutation lane only runs this file):
    df=1 must be legal (Lt→LtE on the df guard flips it), x=0 inclusive
    boundary, and the WH z-formula agrees with the alpha=0.001 table."""
    from app.experiments.services.analysis import chi2_sf

    for df, crit in ((1, 10.828), (4, 18.467), (9, 27.877)):
        assert 0.0003 < chi2_sf(crit, df) < 0.003, df
    assert chi2_sf(0.0, 3) == 1.0
    assert 0.0 < chi2_sf(5e-324, 3) < 1.0  # strictly-positive x takes the WH path
    import pytest as _pytest

    with _pytest.raises(ValueError):
        chi2_sf(1.0, 0)


def test_pool_stratified_weight_sum_overflow_returns_none():
    """Two individually-finite huge weights whose SUM overflows must yield
    None, not an inf-poisoned pooled effect (guards the weight_total
    isfinite check — the ledger twin of fuzz defect #27)."""
    from app.experiments.services.analysis import pool_stratified

    tiny_se = 3.7e-155  # weight ≈ 7.3e308: finite alone, inf when doubled
    assert pool_stratified([(0.0, tiny_se), (0.0, tiny_se)]) is None


# Verified-equivalent survivors (ledger):
# - thompson_weights `sample > best_sample` → GtE: beta samples are
#   continuous; exact ties have measure zero under a seeded PRNG.
# - pool_stratified `se > 0` after sqrt(1/weight_total): weight_total is
#   finite and positive there, so the sqrt is always > 0 — unreachable flip.
# - pool_stratified `weight_total <= 0` → Lt: weights are all positive, so
#   the == 0 edge is unreachable (kept for defensive symmetry). The usable-
#   filter And→Or / se Gt→GtE flips are equivalent too: a zero/denormal se
#   or a non-finite effect is always caught again by the weight / e*weight /
#   pooled-result finiteness gates downstream.
# - aa_probe round(chi2, 3→4): chi2 is an integer/200, so it never has a
#   fourth decimal digit — mathematically equivalent.


def test_thompson_weights_golden_vector():
    """Exact golden output for the default (draws=4000, seed=42) — a silent
    change to either default, or to the posterior parameterization, shifts
    these digits (the mutation lane's default-parameter killer)."""
    from app.experiments.services.analysis import thompson_weights

    result = thompson_weights({"a": (10, 100), "b": (11, 100)})
    assert result["p_best"] == {"a": 0.4125, "b": 0.5875}
    assert result["suggested_weights_bp"] == {"a": 4125, "b": 5875}
    assert result["draws"] == 4000


def test_thompson_weights_filter_exact():
    """The usable-arm filter drops EXACTLY the corrupt arms: n == 0,
    negative successes, successes > n — each boundary pinned."""
    from app.experiments.services.analysis import thompson_weights

    result = thompson_weights({
        "zero_n": (0, 0),
        "neg_s": (-1, 10),
        "over_s": (11, 10),
        "ok1": (2, 10),
        "ok2": (5, 10),
    })
    assert set(result["p_best"]) == {"ok1", "ok2"}
    # boundary inclusions: s == 0 and s == n are both legal
    edge = thompson_weights({"all_fail": (0, 10), "all_pass": (10, 10)})
    assert set(edge["p_best"]) == {"all_fail", "all_pass"}
    assert edge["p_best"]["all_pass"] > 0.99


def test_pool_stratified_extreme_value_paths():
    from app.experiments.services.analysis import pool_stratified

    # denormal se: weight overflows to inf and the stratum is DROPPED, never
    # divided by zero (the se*se > 0 branch must stay strict)
    result = pool_stratified([(1.0, 5e-324), (2.0, 1.0), (3.0, 1.0)])
    assert result is not None and result["strata"] == 2
    assert abs(result["effect"] - 2.5) < 1e-12

    # huge effect x FINITE weight: e*weight alone overflows — that stratum
    # is dropped while the sane ones still pool (weight ≈ 1.5, finite)
    result = pool_stratified([(1.7e308, 0.8165), (1.0, 1.0), (2.0, 1.0)])
    assert result is not None and result["strata"] == 2
    assert abs(result["effect"] - 1.5) < 1e-12

    # every e*weight finite but their SUM overflows with a finite
    # weight_total: the pooled effect would be inf — refused as a whole
    assert pool_stratified([(9e307, 0.7071), (9e307, 0.7071)]) is None


# ── did_estimate (v2 batch 28, quasi-experiments) ────────────────────


def test_did_estimate_change_score_math():
    """Hand-computed golden: control changes 1→2 (Δ=1), treatment 1→4 (Δ=3)
    with tiny within-arm variance → DiD effect 2, significant."""
    from app.experiments.services.analysis import did_estimate

    def _arm(pre: list[float], post: list[float]) -> dict:
        n = len(pre)
        return {
            "n": n, "sum": sum(post), "sum_sq": sum(v * v for v in post),
            "cov_sum": sum(pre), "cov_sum_sq": sum(v * v for v in pre),
            "cov_xy_sum": sum(a * b for a, b in zip(pre, post, strict=True)),
        }

    control = _arm(pre=[1.0, 1.1, 0.9, 1.0], post=[2.0, 2.1, 1.9, 2.0])
    treatment = _arm(pre=[1.0, 0.9, 1.1, 1.0], post=[4.0, 3.9, 4.1, 4.0])
    result = did_estimate(control, treatment)
    assert abs(result["effect"] - 2.0) < 1e-9
    assert result["p"] < 0.001
    assert result["ci"][0] < 2.0 < result["ci"][1]


def test_did_estimate_totality():
    from app.experiments.services.analysis import did_estimate

    assert did_estimate({}, {}) is None  # missing sufficient stats
    tiny = {"n": 1, "sum": 1.0, "sum_sq": 1.0, "cov_sum": 1.0,
            "cov_sum_sq": 1.0, "cov_xy_sum": 1.0}
    assert did_estimate(tiny, tiny) is None  # n < 2
    # zero-variance arms: exact effect, degenerate CI, p None (not a crash)
    flat = {"n": 3, "sum": 6.0, "sum_sq": 12.0, "cov_sum": 3.0,
            "cov_sum_sq": 3.0, "cov_xy_sum": 6.0}
    result = did_estimate(flat, flat)
    assert result["effect"] == 0.0
    assert result["p"] is None


def test_required_n_per_arm_known_value_and_monotonicity():
    """Round 46: two-proportion sample size. Classic worked example —
    baseline 10%, relative MDE 20% (10% -> 12%), alpha .05, power .8 —
    lands near the textbook ~3,8xx per arm; exact integer ledgered from the
    formula itself (normal approximation, pooled-H0/unpooled-H1)."""
    from app.experiments.services.analysis import required_n_per_arm

    n = required_n_per_arm(0.10, 0.20)
    assert 3600 < n < 4100
    assert n == required_n_per_arm(0.10, 0.20)  # deterministic
    # more power -> more units; bigger MDE -> fewer; stricter alpha -> more
    assert required_n_per_arm(0.10, 0.20, power=0.9) > n
    assert required_n_per_arm(0.10, 0.40) < n
    assert required_n_per_arm(0.10, 0.20, alpha=0.01) > n
    # degenerate inputs refuse instead of lying
    assert required_n_per_arm(0.0, 0.2) is None
    assert required_n_per_arm(0.9, 0.2) is None   # lifted rate >= 1
    assert required_n_per_arm(0.5, 0.0) is None   # no difference to detect
    # exact boundaries (wave-12 survivors): the OPEN interval ends refuse
    assert required_n_per_arm(1.0, -0.5) is None  # p1 == 1 exactly
    assert required_n_per_arm(0.5, 1.0) is None   # p2 == 1 exactly
    # exact value pin (kills the sqrt-argument and exponent mutants) — the
    # formula's own output at the textbook point, ledgered as a constant
    assert required_n_per_arm(0.10, 0.20) == 3841


def _mc_arm_stats(ys, xs_by_key, keys):
    cov = {}
    for i, k in enumerate(keys):
        xs = xs_by_key[k]
        entry = {
            "sum": sum(xs),
            "sum_sq": sum(v * v for v in xs),
            "xy_sum": sum(a * b for a, b in zip(ys, xs, strict=True)),
        }
        xx = {}
        for k2 in keys[i + 1:]:
            xs2 = xs_by_key[k2]
            xx[k2] = sum(a * b for a, b in zip(xs, xs2, strict=True))
        if xx:
            entry["xx"] = xx
        cov[k] = entry
    return {"n": len(ys), "sum": sum(ys),
            "sum_sq": sum(v * v for v in ys), "covariates": cov}


def test_multi_cuped_matches_per_unit_oracle():
    """§4.6 v3 round 115: the sufficient-stats implementation must agree with
    an EXPLICIT per-unit residualization oracle — pooled centered OLS theta,
    Z = y - theta·(x - x̄), Welch over Z — on a two-covariate fixture with
    correlated covariates."""
    from app.experiments.services.analysis import (
        multi_cuped_adjusted_welch,
        welch_from_stats,
    )

    keys = ["c1", "c2"]
    cy = [5.0, 7.0, 6.0, 9.0, 4.0, 8.0]
    cx1 = [1.0, 2.0, 1.5, 3.0, 0.5, 2.5]
    cx2 = [0.0, 1.0, 1.0, 2.0, 0.0, 2.0]
    ty = [7.5, 9.0, 8.0, 11.0, 6.0, 10.5]
    tx1 = [1.2, 2.2, 1.4, 3.1, 0.6, 2.6]
    tx2 = [0.0, 1.0, 1.0, 2.0, 1.0, 2.0]

    control = _mc_arm_stats(cy, {"c1": cx1, "c2": cx2}, keys)
    treatment = _mc_arm_stats(ty, {"c1": tx1, "c2": tx2}, keys)
    result = multi_cuped_adjusted_welch(control, treatment, keys)
    assert result is not None and "insufficient_data" not in result

    # oracle: explicit per-unit computation
    ally = cy + ty
    allx = {"c1": cx1 + tx1, "c2": cx2 + tx2}
    n = len(ally)
    ybar = sum(ally) / n
    xbar = {k: sum(allx[k]) / n for k in keys}
    # centered normal equations solved by hand (2x2)
    a11 = sum((v - xbar["c1"]) ** 2 for v in allx["c1"])
    a22 = sum((v - xbar["c2"]) ** 2 for v in allx["c2"])
    a12 = sum((p - xbar["c1"]) * (q - xbar["c2"])
              for p, q in zip(allx["c1"], allx["c2"], strict=True))
    b1 = sum((p - xbar["c1"]) * (y - ybar)
             for p, y in zip(allx["c1"], ally, strict=True))
    b2 = sum((q - xbar["c2"]) * (y - ybar)
             for q, y in zip(allx["c2"], ally, strict=True))
    det = a11 * a22 - a12 * a12
    th1 = (b1 * a22 - b2 * a12) / det
    th2 = (b2 * a11 - b1 * a12) / det
    assert result["theta"]["c1"] == pytest.approx(th1, rel=1e-9)
    assert result["theta"]["c2"] == pytest.approx(th2, rel=1e-9)

    def residuals(ys, x1s, x2s):
        return [
            y - th1 * (p - xbar["c1"]) - th2 * (q - xbar["c2"])
            for y, p, q in zip(ys, x1s, x2s, strict=True)
        ]

    zc = residuals(cy, cx1, cx2)
    zt = residuals(ty, tx1, tx2)
    oracle = welch_from_stats(
        len(zc), sum(zc), sum(v * v for v in zc),
        len(zt), sum(zt), sum(v * v for v in zt),
    )
    assert result["effect"] == pytest.approx(oracle["effect"], rel=1e-9)
    assert result["t"] == pytest.approx(oracle["t"], rel=1e-9)
    assert result["p"] == pytest.approx(oracle["p"], rel=1e-9)
    # round 123: the honesty readout mirrors the single path — achieved
    # variance reduction vs the UNADJUSTED Welch, from the same residuals
    raw = welch_from_stats(
        len(cy), sum(cy), sum(v * v for v in cy),
        len(ty), sum(ty), sum(v * v for v in ty),
    )
    expected_pct = 100.0 * (
        1.0
        - (oracle["control"]["var"] + oracle["treatment"]["var"])
        / (raw["control"]["var"] + raw["treatment"]["var"])
    )
    assert result["variance_reduction_pct"] == pytest.approx(expected_pct, rel=1e-9)
    assert result["variance_reduction_pct"] > 0  # correlated fixture must help


def test_multi_cuped_k1_reduces_to_single_cuped():
    """k == 1 must agree with the existing cuped_adjusted_welch exactly."""
    from app.experiments.services.analysis import (
        cuped_adjusted_welch,
        multi_cuped_adjusted_welch,
    )

    cy = [5.0, 7.0, 6.0, 9.0]
    cx = [1.0, 2.0, 1.5, 3.0]
    ty = [7.5, 9.0, 8.0, 11.0]
    tx = [1.2, 2.2, 1.4, 3.1]
    control = _mc_arm_stats(cy, {"c1": cx}, ["c1"])
    treatment = _mc_arm_stats(ty, {"c1": tx}, ["c1"])
    multi = multi_cuped_adjusted_welch(control, treatment, ["c1"])
    single = cuped_adjusted_welch(
        {"n": 4, "sum": sum(cy), "sum_sq": sum(v * v for v in cy),
         "cov_sum": sum(cx), "cov_sum_sq": sum(v * v for v in cx),
         "cov_xy_sum": sum(a * b for a, b in zip(cy, cx, strict=True))},
        {"n": 4, "sum": sum(ty), "sum_sq": sum(v * v for v in ty),
         "cov_sum": sum(tx), "cov_sum_sq": sum(v * v for v in tx),
         "cov_xy_sum": sum(a * b for a, b in zip(ty, tx, strict=True))},
    )
    assert multi is not None and single is not None
    assert multi["effect"] == pytest.approx(single["effect"], rel=1e-9)
    assert multi["t"] == pytest.approx(single["t"], rel=1e-9)
    assert multi["theta"]["c1"] == pytest.approx(single["theta"], rel=1e-9)
    assert multi["variance_reduction_pct"] == pytest.approx(
        single["variance_reduction_pct"], rel=1e-9
    )


def _hist_of(values: list[float]) -> dict:
    """Build the §4.14 base-2 log histogram the way a source would."""
    import math as _math

    hist: dict = {}
    for v in values:
        if v < 0:
            key = "__neg__"
        elif v == 0:
            key = "__zero__"
        else:
            key = str(max(-20, min(43, _math.floor(_math.log2(v)))))
        hist[key] = hist.get(key, 0) + 1
    return hist


def test_histogram_quantile_brackets_the_true_sample_quantile():
    """Log buckets lose precision but may never lose ORDER: the estimate
    must land within the bucket bounds that contain the true sample
    quantile, for every p across a spread of scales."""
    import math as _math

    from app.experiments.services.analysis import histogram_quantile

    values = sorted([0.7, 1.3, 2.9, 3.3, 5.1, 9.8, 17.0, 33.0, 64.5, 130.0,
                     250.0, 400.0, 700.0, 1500.0, 2900.0, 6000.0])
    hist = _hist_of(values)
    for p in (0.1, 0.25, 0.5, 0.75, 0.9, 0.95):
        out = histogram_quantile(hist, p)
        assert out is not None and out["n"] == len(values)
        # fractional-rank estimator: bracket by the two neighboring order
        # statistics' bucket bounds (floor-rank value's bucket floor, the
        # ceil-rank value's bucket ceiling)
        rank = min(max(p * len(values), 1.0), float(len(values)))
        lo_q = values[_math.floor(rank) - 1]
        hi_q = values[_math.ceil(rank) - 1]
        lo = 2.0 ** _math.floor(_math.log2(lo_q))
        hi = 2.0 ** (_math.floor(_math.log2(hi_q)) + 1)
        assert lo <= out["estimate"] <= hi, (p, out["estimate"], (lo, hi))
        assert out["ci"][0] <= out["estimate"] <= out["ci"][1]


def test_histogram_quantile_exact_pins_and_refusals():
    from app.experiments.services.analysis import histogram_quantile

    # hand histogram: 4 values in bucket 1 ([2,4)), 4 in bucket 3 ([8,16))
    hist = {"1": 4, "3": 4}
    out = histogram_quantile(hist, 0.5)
    # rank 4.0 of 8 -> last of bucket 1: frac 4/4=1 -> exactly hi = 4.0
    assert out is not None and out["estimate"] == pytest.approx(4.0)
    # p -> 1 pushes into bucket 3's upper half
    hi = histogram_quantile(hist, 0.95)
    assert hi is not None and 8.0 <= hi["estimate"] <= 16.0
    # zeros are real rank mass at 0.0
    zed = histogram_quantile({"__zero__": 6, "3": 2}, 0.5)
    assert zed is not None and zed["estimate"] == 0.0
    # refusals: negatives, tiny n, p bounds, empty
    assert histogram_quantile({"__neg__": 1, "3": 5}, 0.5) is None
    assert histogram_quantile({"3": 1}, 0.5) is None
    assert histogram_quantile({"3": 5}, 0.0) is None
    assert histogram_quantile({"3": 5}, 1.0) is None
    assert histogram_quantile({}, 0.5) is None


def test_hist_rank_walk_exact_pins():
    """Wave-19 kills: the rank walk's every operator pinned by hand.
    Empty entries refuse; a rank exactly ON a cumulative boundary belongs
    to the bucket that CLOSES there (frac 1 -> the bucket's hi bound), not
    the next one; clamping lands on the last value."""
    from app.experiments.services.analysis import _hist_value_at_rank

    assert _hist_value_at_rank([], 1.0) is None
    # boundary rank: entries (bucket 0 x2, bucket 5 x1), rank exactly 2.0
    # -> closes bucket 0 -> hi = 2.0 (the >= edge; > would give 32.0)
    assert _hist_value_at_rank([(0, 2), (5, 1)], 2.0) == pytest.approx(2.0)
    # over-total rank clamps to the last rank
    assert _hist_value_at_rank([(2, 1)], 5.0) == pytest.approx(8.0)


def test_histogram_quantile_exact_ci_arithmetic():
    """CI rank bounds np ± z·sqrt(np(1-p)) mapped through the histogram —
    every constant pinned by hand on an unclamped fixture (n=100, one
    bucket, so value = 8·2^(rank/100) exactly)."""
    import math as _math

    from app.experiments.services.analysis import histogram_quantile

    out = histogram_quantile({"3": 100}, 0.5)
    assert out is not None
    z = 1.959963984540054
    half = z * _math.sqrt(100 * 0.25)
    assert out["estimate"] == pytest.approx(8.0 * 2.0 ** (50.0 / 100.0), rel=1e-12)
    assert out["ci"][0] == pytest.approx(8.0 * 2.0 ** ((50.0 - half) / 100.0), rel=1e-12)
    assert out["ci"][1] == pytest.approx(8.0 * 2.0 ** ((50.0 + half) / 100.0), rel=1e-12)
    # n == 2 exactly is admissible (the n < 2 floor, both operator and const)
    assert histogram_quantile({"3": 2}, 0.5) is not None
    # a rank exactly AT the zero mass boundary reads 0.0 (<= edge) ...
    zed = histogram_quantile({"__zero__": 4, "3": 4}, 0.5)
    assert zed is not None and zed["estimate"] == 0.0
    # ... and one past it interpolates the data buckets (rank-zeros, not +)
    past = histogram_quantile({"__zero__": 4, "3": 4}, 0.75)
    assert past is not None
    assert past["estimate"] == pytest.approx(8.0 * 2.0 ** (2.0 / 4.0), rel=1e-12)


def test_quantile_comparison_exact_ci_combination():
    """The combined CI subtracts OPPOSITE ends — pinned by hand on
    unclamped one-bucket arms (control 8·2^f, treatment 64·2^f)."""
    import math as _math

    from app.experiments.services.analysis import quantile_comparison

    out = quantile_comparison({"3": 100}, {"6": 100}, 0.5)
    assert out is not None
    z = 1.959963984540054
    half = z * _math.sqrt(100 * 0.25)
    c_lo = 8.0 * 2.0 ** ((50.0 - half) / 100.0)
    c_hi = 8.0 * 2.0 ** ((50.0 + half) / 100.0)
    t_lo = 64.0 * 2.0 ** ((50.0 - half) / 100.0)
    t_hi = 64.0 * 2.0 ** ((50.0 + half) / 100.0)
    mid_c = 8.0 * 2.0 ** 0.5
    mid_t = 64.0 * 2.0 ** 0.5
    assert out["diff"] == pytest.approx(mid_t - mid_c, rel=1e-12)
    assert out["ci"][0] == pytest.approx(t_lo - c_hi, rel=1e-12)
    assert out["ci"][1] == pytest.approx(t_hi - c_lo, rel=1e-12)


def test_quantile_comparison_diff_and_conservative_ci():
    from app.experiments.services.analysis import (
        histogram_quantile,
        quantile_comparison,
    )

    control = _hist_of([10.0] * 20 + [12.0] * 20)
    treatment = _hist_of([20.0] * 20 + [24.0] * 20)
    out = quantile_comparison(control, treatment, 0.5)
    assert out is not None
    c = histogram_quantile(control, 0.5)
    t = histogram_quantile(treatment, 0.5)
    assert out["diff"] == pytest.approx(t["estimate"] - c["estimate"])
    # conservative combine: subtracting opposite ends can only widen
    assert out["ci"][0] <= out["diff"] <= out["ci"][1]
    assert out["ci"][1] - out["ci"][0] >= (
        (t["ci"][1] - t["ci"][0]) + (c["ci"][1] - c["ci"][0])
    ) - 1e-12
    # either side refusing refuses the comparison
    assert quantile_comparison({"__neg__": 2}, treatment, 0.5) is None


def test_multi_cuped_degenerate_refusals():
    """Collinear covariates -> singular normal equations -> None; a missing
    cross term -> None."""
    from app.experiments.services.analysis import multi_cuped_adjusted_welch

    keys = ["c1", "c2"]
    cy = [5.0, 7.0, 6.0]
    cx = [1.0, 2.0, 1.5]
    control = _mc_arm_stats(cy, {"c1": cx, "c2": cx}, keys)  # identical -> collinear
    treatment = _mc_arm_stats([7.0, 9.0, 8.0], {"c1": cx, "c2": cx}, keys)
    assert multi_cuped_adjusted_welch(control, treatment, keys) is None

    # an arm missing a WHOLE covariate entry refuses cleanly (never crashes)
    whole_missing_c = _mc_arm_stats(cy, {"c1": cx, "c2": [0.0, 1.0, 2.0]}, keys)
    del whole_missing_c["covariates"]["c2"]
    whole_missing_t = _mc_arm_stats([7.0, 9.0, 8.0],
                                    {"c1": cx, "c2": [1.0, 0.0, 2.0]}, keys)
    assert multi_cuped_adjusted_welch(whole_missing_c, whole_missing_t, keys) is None

    # n == 2 per arm is the exact admissible floor (> 1)
    tiny_c = _mc_arm_stats([5.0, 7.0], {"c1": [1.0, 2.0], "c2": [0.0, 1.0]}, keys)
    tiny_t = _mc_arm_stats([8.0, 11.0], {"c1": [1.1, 2.2], "c2": [1.0, 0.0]}, keys)
    assert multi_cuped_adjusted_welch(tiny_c, tiny_t, keys) is not None

    good_c = _mc_arm_stats(cy, {"c1": cx, "c2": [0.0, 1.0, 2.0]}, keys)
    good_t = _mc_arm_stats([7.0, 9.0, 8.0],
                        {"c1": cx, "c2": [1.0, 0.0, 2.0]}, keys)
    del good_c["covariates"]["c1"]["xx"]  # missing cross term
    assert multi_cuped_adjusted_welch(good_c, good_t, keys) is None


def test_aa_calibration_monte_carlo():
    """Round 151 — CALIBRATION, not point correctness: under the null
    (A/A), the frequentist p must be ~uniform and the always-valid mSPRT p
    must be CONSERVATIVE. Deterministic seed; 400 replications of n=100
    per arm. Bounds are generous (3-sigma-ish on the binomial count) so
    the test pins calibration bugs, not sampling noise."""
    import random

    from app.experiments.services.analysis import (
        analyze_binary,
        msprt_always_valid_p,
        welch_from_stats,
    )

    rng = random.Random(42)
    reps = 400
    n = 100
    welch_fp = 0
    msprt_fp = 0
    binary_fp = 0
    for _ in range(reps):
        a = [rng.gauss(10.0, 2.0) for _ in range(n)]
        b = [rng.gauss(10.0, 2.0) for _ in range(n)]
        w = welch_from_stats(
            n, sum(a), sum(v * v for v in a),
            n, sum(b), sum(v * v for v in b),
        )
        if w["p"] < 0.05:
            welch_fp += 1
        if msprt_always_valid_p(w["t"]) < 0.05:
            msprt_fp += 1
        xa = sum(1 for _ in range(n) if rng.random() < 0.3)
        xb = sum(1 for _ in range(n) if rng.random() < 0.3)
        if analyze_binary(xa, n, xb, n).get("p", 1.0) < 0.05:
            binary_fp += 1
    # CUPED under the null with a REAL covariate (x correlates with y but
    # arms are identical): the adjustment must stay calibrated too
    from app.experiments.services.analysis import cuped_adjusted_welch

    cuped_fp = 0
    for _ in range(reps):
        def arm():
            xs = [rng.gauss(5.0, 1.0) for _ in range(n)]
            ys = [x + rng.gauss(0.0, 1.0) for x in xs]
            return {
                "n": n, "sum": sum(ys), "sum_sq": sum(v * v for v in ys),
                "cov_sum": sum(xs), "cov_sum_sq": sum(v * v for v in xs),
                "cov_xy_sum": sum(a * b for a, b in zip(ys, xs, strict=True)),
            }
        out = cuped_adjusted_welch(arm(), arm())
        if out is not None and out["p"] < 0.05:
            cuped_fp += 1

    # nominal 5%: expect ~20/400; 3 sigma ≈ 13 — allow [5, 40]
    assert 5 <= welch_fp <= 40, welch_fp
    assert 5 <= binary_fp <= 40, binary_fp
    assert cuped_fp <= 40, cuped_fp  # the adjustment must not inflate alpha
    # always-valid p is strictly conservative at a single look: fewer
    # rejections than the fixed-horizon test, and never above nominal
    assert msprt_fp <= welch_fp
    assert msprt_fp <= 20, msprt_fp


def test_power_calibration_closes_the_design_loop():
    """Round 152 — the design-time formula and the runtime test must agree:
    simulate binary A/B at exactly required_n_per_arm(baseline, mde) and
    the detection rate must reach the promised power (within a Monte-Carlo
    band). This closes the loop: a drift in EITHER the planner or the test
    breaks it."""
    import random

    from app.experiments.services.analysis import (
        analyze_binary,
        required_n_per_arm,
    )

    baseline = 0.10
    mde = 0.20  # relative: treatment rate 0.12
    n = required_n_per_arm(baseline, mde)
    assert n == 3841  # the round-46 pin — the planner itself is stable

    rng = random.Random(7)
    reps = 200
    detected = 0
    for _ in range(reps):
        xa = sum(1 for _ in range(n) if rng.random() < baseline)
        xb = sum(1 for _ in range(n) if rng.random() < baseline * (1 + mde))
        if analyze_binary(xa, n, xb, n).get("p", 1.0) < 0.05:
            detected += 1
    # promised power 0.8 at the EXACT boundary n; binomial 3 sigma on 200
    # reps ≈ 17 — accept [0.70, 0.92]
    assert 140 <= detected <= 184, detected


def test_msprt_anytime_validity_under_continuous_peeking():
    """Round 153 — the always-valid promise ITSELF: peek after every batch
    and reject the moment p < alpha; across the WHOLE monitored run the
    null rejection rate must stay at or below alpha (plus Monte-Carlo
    slack). A fixed-horizon test peeked this way inflates alpha several
    fold — the companion count demonstrates the contrast, which also makes
    the msprt bound non-vacuous."""
    import random

    from app.experiments.services.analysis import (
        msprt_always_valid_p,
        welch_from_stats,
    )

    rng = random.Random(11)
    reps = 300
    batch, looks = 25, 12  # n per arm grows 25..300 in 12 peeks
    msprt_fp = 0
    naive_fp = 0
    for _ in range(reps):
        a: list[float] = []
        b: list[float] = []
        msprt_hit = False
        naive_hit = False
        for _look in range(looks):
            a.extend(rng.gauss(0.0, 1.0) for _ in range(batch))
            b.extend(rng.gauss(0.0, 1.0) for _ in range(batch))
            w = welch_from_stats(
                len(a), sum(a), sum(v * v for v in a),
                len(b), sum(b), sum(v * v for v in b),
            )
            if msprt_always_valid_p(w["t"]) < 0.05:
                msprt_hit = True
            if w["p"] < 0.05:
                naive_hit = True
        msprt_fp += msprt_hit
        naive_fp += naive_hit
    # alpha 0.05 over 300 reps -> 15 expected at MOST (anytime-valid means
    # the WHOLE monitored run counts as one test); 3 sigma ≈ 11
    assert msprt_fp <= 26, msprt_fp
    # the naive peeker must inflate well past nominal — this contrast is
    # what the always-valid machinery buys (and proves the sim has teeth)
    assert naive_fp > msprt_fp
    assert naive_fp >= 30, naive_fp


def test_quantile_ci_coverage_is_conservative():
    """Round 154 (calibration part 4): the order-statistic CI must COVER the
    true quantile at >= nominal 95% — log-bucket coarsening only WIDENS the
    bracket, so coverage must not fall below the binomial baseline. Skewed
    lognormal data, deterministic seed."""
    import math
    import random

    from app.experiments.services.analysis import histogram_quantile

    rng = random.Random(23)
    reps = 300
    n = 400
    true_p95 = math.exp(1.0 + 0.8 * 1.6448536269514722)  # lognormal(1, .8)
    covered = 0
    for _ in range(reps):
        values = [math.exp(rng.gauss(1.0, 0.8)) for _ in range(n)]
        hist: dict = {}
        for v in values:
            key = str(max(-20, min(43, math.floor(math.log2(v)))))
            hist[key] = hist.get(key, 0) + 1
        out = histogram_quantile(hist, 0.95)
        assert out is not None
        lo, hi = out["ci"]
        # bucket resolution: widen the bracket to the enclosing bucket
        # bounds, which is exactly what the estimate's granularity promises
        lo_bound = 2.0 ** math.floor(math.log2(lo)) if lo > 0 else 0.0
        hi_bound = 2.0 ** (math.floor(math.log2(hi)) + 1)
        if lo_bound <= true_p95 <= hi_bound:
            covered += 1
    # 95% nominal, conservative by construction; 3 sigma on 300 reps ≈ 11
    assert covered >= 274, covered


def test_its_estimate_exact_on_piecewise_linear_data():
    """Round 177 oracle: on EXACT piecewise-linear data the segmented OLS
    recovers the level and trend changes to machine precision (pre slope 1
    from intercept 1; post jumps to 10 with slope 2 at t0=5 -> level
    change 4, trend change 1; zero residuals -> se 0, p 1)."""
    from app.experiments.services.analysis import its_estimate

    pre = [1.0 + t for t in range(5)]
    post = [10.0 + 2.0 * i for i in range(5)]
    out = its_estimate(pre, post)
    assert out is not None
    assert out["level_change"]["estimate"] == pytest.approx(4.0, abs=1e-9)
    assert out["trend_change"]["estimate"] == pytest.approx(1.0, abs=1e-9)
    # float residuals ~1e-15 make se tiny, not zero: p is EXTREME, and the
    # literal se==0 branch stays as defense for exact-integer inputs
    assert out["level_change"]["p"] < 1e-12
    assert out["n_pre"] == 5 and out["n_post"] == 5
    assert "association only" in out["caveat"]


def test_its_estimate_significance_and_refusals():
    """A real jump over noisy-but-deterministic data is significant; a flat
    series is not; under 3 points per side refuses."""
    from app.experiments.services.analysis import its_estimate

    wiggle = [0.05, -0.04, 0.02, -0.03, 0.01, 0.04, -0.02, 0.03, -0.05, 0.02]
    pre = [2.0 + 0.1 * t + wiggle[t] for t in range(5)]
    post = [8.0 + 0.1 * (5 + i) + wiggle[5 + i] for i in range(5)]
    jump = its_estimate(pre, post)
    assert jump is not None
    assert jump["level_change"]["p"] < 0.01
    assert jump["dof"] == 6  # n - 4: the dof arithmetic pinned
    assert jump["level_change"]["estimate"] == pytest.approx(6.0, abs=0.2)

    flat_pre = [1.0 + wiggle[t] for t in range(5)]
    flat_post = [1.0 + wiggle[5 + i] for i in range(5)]
    flat = its_estimate(flat_pre, flat_post)
    assert flat is not None
    assert flat["level_change"]["p"] > 0.2

    assert its_estimate([1.0, 2.0], [3.0, 4.0, 5.0]) is None
    assert its_estimate([1.0, 2.0, 3.0], [4.0, 5.0]) is None
    # EXACTLY 3 points per side is admissible (the < 3 floor, operator AND
    # constant), and the reported dof is n - 4
    minimal = its_estimate([1.0, 2.0, 3.0], [9.0, 10.0, 11.0])
    assert minimal is not None
    assert minimal["dof"] == 2
    assert minimal["level_change"]["estimate"] == pytest.approx(5.0, abs=1e-9)


def test_km_curve_matches_hand_computation():
    """Round 181 oracle: the textbook product-limit example by hand —
    n0=4; day 1: one event (S=3/4); day 2: one censoring (risk set 2);
    day 3: one event (S = 3/4 * 1/2 = 3/8). Greenwood by hand:
    V = S^2 * (1/(4*3) + 1/(2*1))."""
    import math as _m

    from app.experiments.services.analysis import km_curve

    out = km_curve({1: 1, 3: 1}, {2: 1}, 4)
    assert out is not None
    assert out["survival"] == pytest.approx(3.0 / 8.0, abs=1e-12)
    expected_se = (3.0 / 8.0) * _m.sqrt(1.0 / 12.0 + 1.0 / 2.0)
    assert out["se"] == pytest.approx(expected_se, abs=1e-12)
    assert out["events"] == 2 and out["censored"] == 1 and out["n0"] == 4
    assert [pt["day"] for pt in out["curve"]] == [1, 3]
    assert out["curve"][0]["survival"] == pytest.approx(0.75)
    assert out["curve"][1]["at_risk"] == 2  # shrunk by the censoring too

    # CENSORING-CORRECTNESS: binary-at-horizon treats the censored unit as
    # a non-event (3/4 would be 2/4 "converted" -> survival-equivalent 0.5);
    # KM says 3/8 for survival -- the whole point of shipping it
    assert out["survival"] != pytest.approx(0.5)


def test_km_refusals_and_compare():
    from app.experiments.services.analysis import km_compare, km_curve

    assert km_curve({}, {}, 10) is None  # no events
    assert km_curve({1: 1}, {}, 1) is None  # n0 < 2
    assert km_curve({1: 5}, {}, 4) is None  # more events than at risk
    assert km_curve({"x": "y"}, {}, 4) is None  # malformed

    control = km_curve({1: 2}, {}, 10)
    treatment = km_curve({1: 6}, {}, 10)
    out = km_compare(control, treatment)
    assert out is not None
    assert out["diff"] == pytest.approx(0.4 - 0.8)
    assert out["p"] < 0.1
    assert out["ci"][0] <= out["diff"] <= out["ci"][1]
    assert "censoring-correct" in out["caveat"]
    assert km_compare(None, treatment) is None
    # exact-SE pin (round 184): combined Greenwood se = sqrt(.016 + .024)
    assert out["se"] == pytest.approx(0.2, abs=1e-12)
    assert out["z"] == pytest.approx(-2.0, abs=1e-9)
    assert out["p"] == pytest.approx(0.0455, abs=1e-3)


def test_km_boundaries_round184():
    """Wave-37 killers: exact boundary pins on the product-limit guards."""
    from app.experiments.services.analysis import km_compare, km_curve

    # n0 == 2 is ADMISSIBLE (the floor is < 2, not <= 2 or < 3)
    out = km_curve({1: 1}, {}, 2)
    assert out is not None and out["survival"] == pytest.approx(0.5)
    assert out["n0"] == 2

    # zero-count event entries are FILTERED (int(v) > 0, not >= 0):
    # an all-zero events dict is "no events" -> refusal
    assert km_curve({1: 0}, {}, 5) is None

    # total death: d == at_risk is valid (S hits 0; Greenwood term skipped,
    # no division by the empty risk set)
    out = km_curve({1: 2}, {}, 2)
    assert out is not None and out["survival"] == 0.0 and out["se"] == 0.0
    assert out["curve"] == [{"day": 1, "survival": 0.0, "at_risk": 2}]

    # anything AFTER the risk set empties (at_risk == 0 exactly) refuses
    assert km_curve({1: 2}, {2: 1}, 2) is None

    # zero-SE compare: two total-death curves -> the degenerate branch
    # (z 0, p 1, point CI), never a division by zero
    cmp_out = km_compare(km_curve({1: 2}, {}, 2), km_curve({1: 3}, {}, 3))
    assert cmp_out is not None
    assert cmp_out["z"] == 0.0 and cmp_out["p"] == 1.0
    assert cmp_out["ci"] == [0.0, 0.0]


def test_synthetic_control_exact_mixture_oracle():
    """Round 194 (§4.16 step 1): treated pre IS 0.5*d0 + 0.5*d1 exactly —
    the simplex fit must find those weights, the pre-fit must be perfect,
    and the post gap reads 4 - (0.5*5 + 0.5*1) = 1.0. Two donors only, so
    placebo inference refuses (needs >= 3)."""
    from app.experiments.services.analysis import synthetic_control

    out = synthetic_control(
        [2.0, 2.0, 2.0, 2.0], [4.0],
        [[1.0, 2.0, 3.0, 4.0], [3.0, 2.0, 1.0, 0.0]],
        [[5.0], [1.0]],
    )
    assert out is not None
    assert out["weights"][0] == pytest.approx(0.5, abs=1e-6)
    assert out["weights"][1] == pytest.approx(0.5, abs=1e-6)
    assert sum(out["weights"]) == pytest.approx(1.0, abs=1e-9)
    assert out["pre_rmspe"] == pytest.approx(0.0, abs=1e-6)
    assert out["gap"] == pytest.approx(1.0, abs=1e-6)
    assert out["placebo_p"] is None and out["donors"] == 2
    assert "association only" in out["caveat"]
    # deterministic: identical calls give identical dicts
    assert out == synthetic_control(
        [2.0, 2.0, 2.0, 2.0], [4.0],
        [[1.0, 2.0, 3.0, 4.0], [3.0, 2.0, 1.0, 0.0]],
        [[5.0], [1.0]],
    )


def test_synthetic_control_placebo_and_refusals():
    from app.experiments.services.analysis import synthetic_control

    out = synthetic_control(
        [1.0, 2.0, 3.0], [4.0],
        [[1.0, 2.0, 3.0], [5.0, 5.0, 4.0], [0.0, 1.0, 1.0]],
        [[4.0], [6.0], [1.0]],
    )
    assert out is not None
    # three donors -> placebo permutation runs; the true ratio tops the
    # placebo ratios here, so p = (1 + 0) / (3 + 1)
    assert out["placebo_p"] == pytest.approx(0.25)
    assert out["rmspe_ratio"] > 1.0

    # refusals: short pre, lone donor, all-constant donor matrix,
    # ragged shapes
    assert synthetic_control([1.0, 2.0], [1.0],
                             [[1.0, 2.0], [2.0, 1.0]], [[1.0], [1.0]]) is None
    assert synthetic_control([1.0, 2.0, 3.0], [1.0],
                             [[1.0, 2.0, 3.0]], [[1.0]]) is None
    assert synthetic_control([1.0, 2.0, 3.0], [1.0],
                             [[2.0, 2.0, 2.0], [2.0, 2.0, 2.0]],
                             [[1.0], [1.0]]) is None
    assert synthetic_control([1.0, 2.0, 3.0], [1.0],
                             [[1.0, 2.0], [2.0, 1.0, 0.0]],
                             [[1.0], [1.0]]) is None
    assert synthetic_control([1.0, 2.0, 3.0], [],
                             [[1.0, 2.0, 3.0], [2.0, 1.0, 0.0]],
                             [[], []]) is None


def test_project_simplex_hand_oracles():
    """Round 197 wave-39 killers: the Duchi projection by hand."""
    from app.experiments.services.analysis import _project_simplex

    assert _project_simplex([0.8, 0.8]) == pytest.approx([0.5, 0.5])
    assert _project_simplex([2.0, 0.0]) == pytest.approx([1.0, 0.0])
    # v = [0.3, 0.1, -0.2]: theta = (0.2 - 1)/3 = -0.2667 by hand
    out = _project_simplex([0.3, 0.1, -0.2])
    assert out == pytest.approx([0.3 + 4.0 / 15.0, 0.1 + 4.0 / 15.0,
                                 -0.2 + 4.0 / 15.0], abs=1e-12)
    assert sum(out) == pytest.approx(1.0, abs=1e-12)
    # already-on-simplex input is a fixed point
    assert _project_simplex([0.25, 0.75]) == pytest.approx([0.25, 0.75])


def test_synthetic_control_placebo_p_is_one_when_fit_is_perfect():
    """Round 197: treated IS donor 0, so the true post fit is exact and the
    true RMSPE ratio is 0 — every placebo ratio ties or beats it, p must be
    EXACTLY (1 + 3) / (3 + 1) = 1.0 (kills the worse-counter and the
    numerator/denominator constant mutants: any drift makes p != 1.0 or
    p > 1)."""
    from app.experiments.services.analysis import synthetic_control

    out = synthetic_control(
        [1.0, 2.0, 3.0], [10.0],
        [[1.0, 2.0, 3.0], [9.0, 8.0, 7.0], [5.0, 5.0, 5.0]],
        [[10.0], [1.0], [5.0]],
    )
    assert out is not None
    assert out["pre_rmspe"] == pytest.approx(0.0, abs=1e-6)
    assert out["post_rmspe"] == pytest.approx(0.0, abs=1e-5)
    assert out["placebo_p"] == pytest.approx(1.0)
    assert out["placebo_p"] <= 1.0


def test_auto_select_covariates_hand_oracle():
    """Round 202 (§4.6b): selection from stored sums alone — strongest
    |r| first, threshold exclusion, degenerate/missing candidates skipped,
    deterministic tie-break by key, max_k cap."""
    from app.experiments.services.analysis import auto_select_covariates

    def arm(n, sy, syy, covs):
        return {"n": n, "sum": sy, "sum_sq": syy, "covariates": covs}

    # strong positive (r ~ 0.976), perfect negative, near-zero, constant
    arms = [
        arm(4, 52.0, 696.0, {
            "strong": {"sum": 10.0, "sum_sq": 30.0, "xy_sum": 140.0},
            "anti": {"sum": -10.0, "sum_sq": 30.0, "xy_sum": -140.0},
            "flat": {"sum": 8.0, "sum_sq": 16.0, "xy_sum": 104.0},
        }),
        arm(4, 56.0, 804.0, {
            "strong": {"sum": 10.0, "sum_sq": 30.0, "xy_sum": 150.0},
            "anti": {"sum": -10.0, "sum_sq": 30.0, "xy_sum": -150.0},
            "flat": {"sum": 8.0, "sum_sq": 16.0, "xy_sum": 112.0},
        }),
    ]
    out = auto_select_covariates(arms, ["strong", "anti", "flat"])
    # |r| equal for strong/anti (same magnitude) -> tie-break by key:
    # "anti" < "strong"; the constant covariate is skipped (zero variance)
    assert out == ["anti", "strong"]

    # threshold: an |r| below 0.1 is excluded
    weak_arms = [
        arm(4, 52.0, 696.0,
            {"weak": {"sum": 10.0, "sum_sq": 30.0, "xy_sum": 130.4}}),
        arm(4, 56.0, 804.0,
            {"weak": {"sum": 10.0, "sum_sq": 30.0, "xy_sum": 140.4}}),
    ]
    # pooled cov = 270.8 - 270 = 0.8 -> r = 0.8/sqrt(420) ~ 0.039 < 0.1
    assert auto_select_covariates(weak_arms, ["weak"]) == []

    # a candidate missing from ANY arm is never guessed at
    partial = [
        arm(4, 52.0, 696.0,
            {"strong": {"sum": 10.0, "sum_sq": 30.0, "xy_sum": 140.0}}),
        arm(4, 56.0, 804.0, {}),
    ]
    assert auto_select_covariates(partial, ["strong"]) == []

    # max_k caps the list
    assert auto_select_covariates(arms, ["strong", "anti"], max_k=1) == ["anti"]


def test_variance_reduction_auto_literal_validation():
    """Round 202: ["auto"] is a reserved lone literal."""
    from app.experiments.schemas import VarianceReductionSpec

    spec = VarianceReductionSpec(method="cuped", covariate_metrics=["auto"])
    assert spec.covariates() == ["auto"]
    with pytest.raises(ValueError):
        VarianceReductionSpec(
            method="cuped", covariate_metrics=["auto", "revision_count"])

    from app.experiments.services.metrics import resolve_covariates
    assert resolve_covariates(spec) == ["practical_pass_rate",
                                        "revision_count"]
