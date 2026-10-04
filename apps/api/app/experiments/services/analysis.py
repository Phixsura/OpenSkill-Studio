"""Pure statistical core (ADR-017 §10). Zero I/O — every function maps
sufficient statistics to results, so the whole module is exhaustively
testable and mutation-hostile.

No scipy: the numeric layer is erfc-based normal, Acklam inverse normal,
a Numerical-Recipes incomplete-beta continued fraction (Student t), and
closed-form/grid Bayesian posteriors. Golden tests pin exact closed forms
(t with df=1/2, defining quadratic of Wilson endpoints, hand-computable
two-proportion examples) rather than trusting reimplementations.

Every comparison reports practical effect + CI first; p-values are
supporting evidence, never the headline (§10).
"""

import math

Z_975 = 1.959963984540054  # norm_ppf(0.975)

# ── Normal distribution ──────────────────────────────────────────────


def norm_cdf(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def norm_sf(x: float) -> float:
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def thompson_weights(
    arms: dict[str, tuple[float, float]], *, draws: int = 4000, seed: int = 42
) -> dict | None:
    """Thompson-sampling allocation suggestion over binary arms (§4.4 v2,
    allocation_mode=bandit): Beta(1+s, 1+f) posteriors, Monte-Carlo p(best)
    per arm, weights in basis points summing to exactly 10000. Seeded — the
    suggestion is deterministic for a given dataset. ADVISORY ONLY: nothing
    auto-applies it; an operator ships new weights as a new version."""
    import random

    usable = {
        key: (float(successes), float(n))
        for key, (successes, n) in arms.items()
        if n > 0 and 0 <= successes <= n
    }
    if len(usable) < 2:
        return None
    rng = random.Random(seed)
    wins = dict.fromkeys(usable, 0)
    for _ in range(draws):
        best_key, best_sample = None, -1.0
        for key, (successes, n) in usable.items():
            sample = rng.betavariate(1.0 + successes, 1.0 + (n - successes))
            if sample > best_sample:
                best_key, best_sample = key, sample
        wins[best_key] += 1
    p_best = {key: count / draws for key, count in wins.items()}
    weights = {key: round(p * 10_000) for key, p in p_best.items()}
    # fix rounding drift onto the current best arm so Σ == 10000 exactly
    drift = 10_000 - sum(weights.values())
    top = max(weights, key=lambda k: weights[k])
    weights[top] += drift
    return {"p_best": p_best, "suggested_weights_bp": weights, "draws": draws}


def did_estimate(control: dict, treatment: dict) -> dict | None:
    """Difference-in-differences from per-unit sufficient stats (§10 v2,
    quasi-experiments): each arm carries the post-period outcome (sum,
    sum_sq) and the PRE-period covariate of the same metric (cov_*) — DiD is
    the fixed-theta=1 change score (y − x), so the arm variance comes from
    Var(y) + Var(x) − 2·Cov(x, y), all derivable from the sufficient stats.
    Association-grade: the parallel-trends assumption is the caller's caveat."""
    required = ("n", "sum", "sum_sq", "cov_sum", "cov_sum_sq", "cov_xy_sum")
    for arm in (control, treatment):
        if any(arm.get(k) is None for k in required):
            return None
    n1, n2 = control["n"], treatment["n"]
    if n1 < 2 or n2 < 2:
        return None

    def _change_stats(arm: dict) -> tuple[float, float]:
        n = arm["n"]
        mean = arm["sum"] / n - arm["cov_sum"] / n
        # Var(y-x) via sums: Σ(y-x)² = Σy² - 2Σxy + Σx²
        sum_sq_change = arm["sum_sq"] - 2.0 * arm["cov_xy_sum"] + arm["cov_sum_sq"]
        var = (sum_sq_change - n * mean * mean) / (n - 1)
        return mean, max(var, 0.0)

    mean1, var1 = _change_stats(control)
    mean2, var2 = _change_stats(treatment)
    effect = mean2 - mean1
    se = math.sqrt(var1 / n1 + var2 / n2)
    if not (math.isfinite(effect) and math.isfinite(se)):
        return None
    if se <= 0:
        return {"effect": effect, "se": 0.0, "ci": [effect, effect], "p": None}
    z = effect / se
    return {
        "effect": effect,
        "se": se,
        "ci": [effect - 1.959963984540054 * se, effect + 1.959963984540054 * se],
        "z": z,
        "p": 2.0 * norm_sf(abs(z)),
    }


def pool_stratified(strata: list[tuple[float, float]]) -> dict | None:
    """Inverse-variance pooling of per-stratum effects (post-stratification,
    §4.6 v2): effect = Σ(e_i/se_i²)/Σ(1/se_i²), se = sqrt(1/Σ(1/se_i²)).
    Strata with non-finite or non-positive se are dropped; needs >= 2 usable
    strata to differ meaningfully from the pooled estimate."""
    # fuzz-found (#27): a denormal se underflows se*se to 0.0 — the weight
    # must itself be finite and positive, not just the se
    usable = []
    for e, se in strata:
        if not (math.isfinite(e) and math.isfinite(se) and se > 0):
            continue
        weight = 1.0 / (se * se) if se * se > 0 else float("inf")
        if math.isfinite(weight) and math.isfinite(e * weight):
            usable.append((e, se, weight))
    if len(usable) < 2:
        return None
    weight_total = sum(w for _e, _se, w in usable)
    if not math.isfinite(weight_total) or weight_total <= 0:
        return None
    effect = sum(e * w for e, _se, w in usable) / weight_total
    se = math.sqrt(1.0 / weight_total)
    if not (math.isfinite(effect) and math.isfinite(se) and se > 0):
        return None
    usable = [(e, s_) for e, s_, _w in usable]
    z = effect / se
    return {
        "effect": effect,
        "se": se,
        "ci": [effect - 1.959963984540054 * se, effect + 1.959963984540054 * se],
        "p": 2.0 * norm_sf(abs(z)),
        "strata": len(usable),
    }


def chi2_sf(x: float, df: int) -> float:
    """Chi-square survival function via the Wilson-Hilferty cube-root normal
    approximation — good to ~1e-3 in the alerting tail for df >= 1, which is
    all the interaction sweep needs (alpha = 0.001 gate, arbitrary df)."""
    if df < 1:
        raise ValueError("df must be >= 1")
    if x <= 0.0:
        return 1.0
    c = 2.0 / (9.0 * df)
    z = ((x / df) ** (1.0 / 3.0) - (1.0 - c)) / math.sqrt(c)
    return norm_sf(z)


def norm_ppf(p: float) -> float:
    """Acklam's rational approximation (|rel err| < 1.15e-9), refined with
    one Halley step against erfc for full double precision."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    a = (-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00)
    b = (-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00)
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    elif p <= p_high:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
            ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1
        )
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    # One Halley refinement
    e = norm_cdf(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


# ── Incomplete beta → Student t ──────────────────────────────────────


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta (Numerical Recipes)."""
    max_iter, eps, fpmin = 200, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_front = (
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: float) -> float:
    """P(T > t) for Student t with df degrees of freedom (t >= 0 or any)."""
    if df <= 0:
        raise ValueError("df must be > 0")
    x = df / (df + t * t)
    p = 0.5 * betainc(df / 2.0, 0.5, x)
    return p if t >= 0 else 1.0 - p


def t_ppf(p: float, df: float) -> float:
    """Inverse of P(T <= t) via bisection (monotone, bounded)."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if 1.0 - t_sf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def beta_ppf(p: float, a: float, b: float) -> float:
    """Beta quantile via bisection on the regularized incomplete beta."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if betainc(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ── Binary outcomes: Wilson + Newcombe + two-proportion z ────────────


def wilson_ci(successes: float, n: float, z: float = Z_975) -> tuple[float, float]:
    if n <= 0:
        return (0.0, 1.0)
    phat = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2.0 * n)) / denom
    half = z * math.sqrt(phat * (1.0 - phat) / n + z2 / (4.0 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def analyze_binary(
    control_successes: float, control_n: float,
    treatment_successes: float, treatment_n: float,
) -> dict:
    """Two-proportion comparison: absolute + relative effect, Newcombe score
    CI on the difference, two-sided pooled-z p-value."""
    if control_n <= 0 or treatment_n <= 0:
        return {"insufficient_data": True}
    p1 = control_successes / control_n
    p2 = treatment_successes / treatment_n
    effect = p2 - p1
    l1, u1 = wilson_ci(control_successes, control_n)
    l2, u2 = wilson_ci(treatment_successes, treatment_n)
    ci = (
        effect - math.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2),
        effect + math.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2),
    )
    pooled = (control_successes + treatment_successes) / (control_n + treatment_n)
    se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / control_n + 1.0 / treatment_n))
    z = effect / se if se > 0 else 0.0
    p_value = 2.0 * norm_sf(abs(z))
    return {
        "effect": effect,
        "relative": (effect / p1) if p1 > 0 else None,
        "ci": list(ci),
        "z": z,
        "se": se,
        "p": p_value,
        "control": {"rate": p1, "ci": [l1, u1], "n": control_n},
        "treatment": {"rate": p2, "ci": [l2, u2], "n": treatment_n},
    }


# ── Continuous outcomes: Welch t from sufficient statistics ──────────


def moments_from_stats(n: float, total: float, total_sq: float) -> tuple[float, float]:
    """(mean, unbiased variance) from n, Σx, Σx²."""
    if n <= 1:
        return (total / n if n else 0.0, 0.0)
    mean = total / n
    var = max(0.0, (total_sq - n * mean * mean) / (n - 1.0))
    return mean, var


def welch_from_stats(
    n1: float, sum1: float, sumsq1: float,
    n2: float, sum2: float, sumsq2: float,
) -> dict:
    """Welch t on (control=1, treatment=2) from sufficient statistics."""
    if n1 <= 1 or n2 <= 1:
        return {"insufficient_data": True}
    m1, v1 = moments_from_stats(n1, sum1, sumsq1)
    m2, v2 = moments_from_stats(n2, sum2, sumsq2)
    se2 = v1 / n1 + v2 / n2
    effect = m2 - m1
    if se2 <= 0:
        return {
            "effect": effect, "relative": (effect / m1) if m1 else None,
            "ci": [effect, effect], "t": 0.0, "df": n1 + n2 - 2, "p": 1.0 if effect == 0 else 0.0,
            "control": {"mean": m1, "var": v1, "n": n1},
            "treatment": {"mean": m2, "var": v2, "n": n2},
        }
    se = math.sqrt(se2)
    t = effect / se
    df = se2 * se2 / ((v1 / n1) ** 2 / (n1 - 1.0) + (v2 / n2) ** 2 / (n2 - 1.0))
    tcrit = t_ppf(0.975, df)
    p_value = 2.0 * t_sf(abs(t), df)
    return {
        "effect": effect,
        "relative": (effect / m1) if m1 else None,
        "ci": [effect - tcrit * se, effect + tcrit * se],
        "t": t,
        "df": df,
        "p": p_value,
        "control": {"mean": m1, "var": v1, "n": n1},
        "treatment": {"mean": m2, "var": v2, "n": n2},
    }


def welch_from_values(control: list[float], treatment: list[float]) -> dict:
    """Cluster-level analysis: each value is one cluster mean; n = cluster
    count — no pseudo-independence (§10 clustered)."""
    return welch_from_stats(
        len(control), sum(control), sum(v * v for v in control),
        len(treatment), sum(treatment), sum(v * v for v in treatment),
    )


# ── Rate outcomes: delta method over events / exposure-time ──────────


def analyze_rate(
    control_events: float, control_exposure: float,
    treatment_events: float, treatment_exposure: float,
) -> dict:
    """Poisson-rate difference; var(rate) ≈ events / exposure² (delta)."""
    if control_exposure <= 0 or treatment_exposure <= 0:
        return {"insufficient_data": True}
    r1 = control_events / control_exposure
    r2 = treatment_events / treatment_exposure
    effect = r2 - r1
    var = control_events / control_exposure**2 + treatment_events / treatment_exposure**2
    se = math.sqrt(var)
    z = effect / se if se > 0 else 0.0
    return {
        "effect": effect,
        "relative": (effect / r1) if r1 > 0 else None,
        "ci": [effect - Z_975 * se, effect + Z_975 * se],
        "se": se,
        "z": z,
        "p": 2.0 * norm_sf(abs(z)),
        "control": {"rate": r1, "events": control_events, "exposure": control_exposure},
        "treatment": {"rate": r2, "events": treatment_events, "exposure": treatment_exposure},
    }


# ── CUPED (§10 v2): sufficient-statistics variance reduction ─────────


def _solve_spd(a: list[list[float]], b: list[float]) -> list[float] | None:
    """Tiny Gaussian elimination with partial pivoting for the k<=3 normal
    equations; None when singular/degenerate."""
    k = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(k):
        pivot = max(range(col, k), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            return None
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(k):
            if r == col:
                continue
            f = m[r][col] / m[col][col]
            for c in range(col, k + 1):
                m[r][c] -= f * m[col][c]
    return [m[i][k] / m[i][i] for i in range(k)]


def multi_cuped_adjusted_welch(
    control: dict, treatment: dict, covariate_keys: list[str]
) -> dict | None:
    """§4.6 v3 (round 115): joint multi-covariate CUPED from per-arm
    sufficient stats. Arms carry {n, sum, sum_sq, covariates: {key: {sum,
    sum_sq, xy_sum, xx: {later_key: sum}}}}. theta is the pooled OLS
    coefficient vector over CENTERED covariates; Z = Y - theta·(X - x_mean)
    analyzed with Welch. k == 1 reduces exactly to cuped_adjusted_welch.
    None when any aggregate is missing or the design is degenerate."""
    k = len(covariate_keys)
    if k == 0:
        return None
    arms = (control, treatment)
    for arm in arms:
        if any(arm.get(f) is None for f in ("n", "sum", "sum_sq")):
            return None
        cov = arm.get("covariates") or {}
        for key in covariate_keys:
            entry = cov.get(key)
            if entry is None or any(
                entry.get(f) is None for f in ("sum", "sum_sq", "xy_sum")
            ):
                return None
    n = control["n"] + treatment["n"]
    if control["n"] <= 1 or treatment["n"] <= 1:
        return None

    def pooled_cov(key: str, field: str) -> float:
        return (control["covariates"][key][field]
                + treatment["covariates"][key][field])

    def pooled_xx(ki: str, kj: str) -> float:
        # upper-triangle storage: the earlier key holds the cross sum
        i, j = covariate_keys.index(ki), covariate_keys.index(kj)
        first, second = (ki, kj) if i < j else (kj, ki)
        total = 0.0
        for arm in arms:
            entry = arm["covariates"][first]
            xx = entry.get("xx") or {}
            if second not in xx:
                return float("nan")
            total += xx[second]
        return total

    sy = control["sum"] + treatment["sum"]
    sx = {key: pooled_cov(key, "sum") for key in covariate_keys}
    x_mean = {key: sx[key] / n for key in covariate_keys}
    # centered normal equations: A[i][j] = S_xixj - n·x̄i·x̄j ; b[i] = S_xiy - n·x̄i·ȳ
    a: list[list[float]] = []
    b: list[float] = []
    y_mean = sy / n
    for i, ki in enumerate(covariate_keys):
        row = []
        for j, kj in enumerate(covariate_keys):
            if i == j:
                s_ij = pooled_cov(ki, "sum_sq")
            else:
                s_ij = pooled_xx(ki, kj)
                if s_ij != s_ij:  # NaN — missing cross term
                    return None
            row.append(s_ij - n * x_mean[ki] * x_mean[kj])
        a.append(row)
        b.append(pooled_cov(ki, "xy_sum") - n * x_mean[ki] * y_mean)
    theta = _solve_spd(a, b)
    if theta is None:
        return None

    def adjusted(arm: dict) -> tuple[float, float, float]:
        an, asy, asyy = arm["n"], arm["sum"], arm["sum_sq"]
        cov = arm["covariates"]
        # ΣZ = Σy − Σ_i θi (Σxi − n·x̄i)
        sz = asy - sum(
            theta[i] * (cov[ki]["sum"] - an * x_mean[ki])
            for i, ki in enumerate(covariate_keys)
        )
        # ΣZ² = Σy² − 2Σθi(Σxiy − x̄iΣy) + ΣΣ θiθj (Σxixj − x̄jΣxi − x̄iΣxj + n·x̄i·x̄j)
        szz = asyy
        for i, ki in enumerate(covariate_keys):
            szz -= 2.0 * theta[i] * (cov[ki]["xy_sum"] - x_mean[ki] * asy)
        for i, ki in enumerate(covariate_keys):
            for j, kj in enumerate(covariate_keys):
                if i == j:
                    s_ij = cov[ki]["sum_sq"]
                elif i < j:
                    s_ij = (cov[ki].get("xx") or {}).get(kj, 0.0)
                else:
                    s_ij = (cov[kj].get("xx") or {}).get(ki, 0.0)
                szz += theta[i] * theta[j] * (
                    s_ij
                    - x_mean[kj] * cov[ki]["sum"]
                    - x_mean[ki] * cov[kj]["sum"]
                    + an * x_mean[ki] * x_mean[kj]
                )
        return an, sz, szz

    n1, s1, ss1 = adjusted(control)
    n2, s2, ss2 = adjusted(treatment)
    result = welch_from_stats(n1, s1, ss1, n2, s2, ss2)
    if result.get("insufficient_data"):
        return None
    # same honesty readout as the single-covariate path: achieved variance
    # reduction vs the unadjusted Welch
    raw = welch_from_stats(
        control["n"], control["sum"], control["sum_sq"],
        treatment["n"], treatment["sum"], treatment["sum_sq"],
    )
    var_raw = raw.get("control", {}).get("var", 0) + raw.get("treatment", {}).get("var", 0)
    var_adj = result.get("control", {}).get("var", 0) + result.get("treatment", {}).get("var", 0)
    result["variance_reduction_pct"] = (
        100.0 * (1.0 - var_adj / var_raw) if var_raw > 0 else 0.0
    )
    result["theta"] = {key: theta[i] for i, key in enumerate(covariate_keys)}
    result["cuped"] = "multi"
    return result


def cuped_adjusted_welch(control: dict, treatment: dict) -> dict | None:
    """CUPED from per-arm sufficient stats:
    {n, sum, sum_sq, cov_sum, cov_sum_sq, cov_xy_sum}.
    theta = pooled cov(X,Y)/var(X); analyze Y - theta·X. Returns None when
    covariate aggregates are missing or degenerate."""
    required = ("n", "sum", "sum_sq", "cov_sum", "cov_sum_sq", "cov_xy_sum")
    for arm in (control, treatment):
        if any(arm.get(k) is None for k in required):
            return None
    n = control["n"] + treatment["n"]
    if control["n"] <= 1 or treatment["n"] <= 1:
        return None
    sx = control["cov_sum"] + treatment["cov_sum"]
    sxx = control["cov_sum_sq"] + treatment["cov_sum_sq"]
    sy = control["sum"] + treatment["sum"]
    sxy = control["cov_xy_sum"] + treatment["cov_xy_sum"]
    var_x_n = sxx - sx * sx / n  # n·var(X)
    if var_x_n <= 0:
        return None
    theta = (sxy - sx * sy / n) / var_x_n
    x_mean = sx / n

    def adjusted(arm: dict) -> tuple[float, float, float]:
        # Z = Y - theta(X - x_mean): ΣZ, ΣZ² from cross sums
        an, asy, asyy = arm["n"], arm["sum"], arm["sum_sq"]
        asx, asxx, asxy = arm["cov_sum"], arm["cov_sum_sq"], arm["cov_xy_sum"]
        sz = asy - theta * (asx - an * x_mean)
        szz = (
            asyy
            - 2.0 * theta * (asxy - x_mean * asy)
            + theta * theta * (asxx - 2.0 * x_mean * asx + an * x_mean * x_mean)
        )
        return an, sz, szz

    n1, s1, ss1 = adjusted(control)
    n2, s2, ss2 = adjusted(treatment)
    result = welch_from_stats(n1, s1, ss1, n2, s2, ss2)
    if result.get("insufficient_data"):
        return None
    raw = welch_from_stats(
        control["n"], control["sum"], control["sum_sq"],
        treatment["n"], treatment["sum"], treatment["sum_sq"],
    )
    var_raw = raw.get("control", {}).get("var", 0) + raw.get("treatment", {}).get("var", 0)
    var_adj = result.get("control", {}).get("var", 0) + result.get("treatment", {}).get("var", 0)
    result["theta"] = theta
    result["variance_reduction_pct"] = (
        100.0 * (1.0 - var_adj / var_raw) if var_raw > 0 else 0.0
    )
    return result


# ── Sequential monitoring ────────────────────────────────────────────


def km_curve(
    events: dict[int, int], censored: dict[int, int], n0: int
) -> dict | None:
    """§4.15 (round 181): product-limit survival over DAY-granular counts —
    S(t) = prod over event days (1 - d_i/n_i) with the risk set shrunk by
    both events and censorings; Greenwood variance for the SE at the
    horizon. Refuses on n0 < 2, no events at all, or malformed counts."""
    if n0 < 2:
        return None
    try:
        event_days = {int(k): int(v) for k, v in events.items() if int(v) > 0}
        censor_days = {int(k): int(v) for k, v in censored.items() if int(v) > 0}
    except (TypeError, ValueError):
        return None
    if not event_days:
        return None
    days = sorted(set(event_days) | set(censor_days))
    at_risk = n0
    survival = 1.0
    greenwood = 0.0
    curve: list[dict] = []
    for day in days:
        d = event_days.get(day, 0)
        c = censor_days.get(day, 0)
        if at_risk <= 0 or d > at_risk or d < 0 or c < 0:
            return None
        if d > 0:
            survival *= 1.0 - d / at_risk
            if at_risk > d:
                greenwood += d / (at_risk * (at_risk - d))
            curve.append({"day": day, "survival": survival, "at_risk": at_risk})
        at_risk -= d + c
    se = survival * math.sqrt(greenwood) if greenwood > 0 else 0.0
    return {
        "survival": survival,
        "se": se,
        "events": sum(event_days.values()),
        "censored": sum(censor_days.values()),
        "n0": n0,
        "curve": curve,
    }


def km_compare(control: dict | None, treatment: dict | None) -> dict | None:
    """Survival difference at the horizon with a normal-approximation CI
    from the Greenwood SEs — censoring-correct, unlike binary-at-horizon,
    which stays the authoritative engine read."""
    if control is None or treatment is None:
        return None
    diff = treatment["survival"] - control["survival"]
    se = math.sqrt(control["se"] ** 2 + treatment["se"] ** 2)
    if se > 0:
        z = diff / se
        p = 2.0 * norm_sf(abs(z))
        ci = [diff - 1.959963984540054 * se, diff + 1.959963984540054 * se]
    else:
        z, p, ci = 0.0, 1.0, [diff, diff]
    return {
        "survival_control": control["survival"],
        "survival_treatment": treatment["survival"],
        "diff": diff,
        "se": se,
        "z": z,
        "p": p,
        "ci": ci,
        "caveat": "Kaplan-Meier at the horizon — censoring-correct; "
                  "the binary-at-horizon engine read stays authoritative",
    }


def its_estimate(pre: list[float], post: list[float]) -> dict | None:
    """§10 v3 (round 177): interrupted time series for OBSERVATIONAL runs —
    segmented OLS y_t = b0 + b1*t + b2*post + b3*(t - t0)*post over daily
    means. Returns the level change (b2) and trend change (b3) with
    classical OLS standard errors; None when either side has < 3 points or
    the design is singular. Association only — the caller attaches the
    causal_claim:false caveat."""
    n_pre, n_post = len(pre), len(post)
    if n_pre < 3 or n_post < 3:
        return None
    ys = [*pre, *post]
    n = len(ys)
    t0 = n_pre  # the interruption sits between pre[-1] and post[0]
    xs = [
        [1.0, float(t), 1.0 if t >= t0 else 0.0,
         float(t - t0) if t >= t0 else 0.0]
        for t in range(n)
    ]
    k = 4
    xtx = [[sum(xs[r][i] * xs[r][j] for r in range(n)) for j in range(k)]
           for i in range(k)]
    xty = [sum(xs[r][i] * ys[r] for r in range(n)) for i in range(k)]
    beta = _solve_spd(xtx, xty)
    if beta is None:
        return None
    residuals = [ys[r] - sum(xs[r][i] * beta[i] for i in range(k))
                 for r in range(n)]
    dof = n - k
    if dof <= 0:
        return None
    sigma2 = sum(e * e for e in residuals) / dof
    # standard errors from the (X'X)^-1 diagonal, via k solves
    ses = []
    for i in range(k):
        unit = [1.0 if j == i else 0.0 for j in range(k)]
        col = _solve_spd(xtx, unit)
        if col is None:
            return None
        ses.append(math.sqrt(max(sigma2 * col[i], 0.0)))
    out = {}
    for name, idx in (("level_change", 2), ("trend_change", 3)):
        est, se = beta[idx], ses[idx]
        if se > 0:
            t_stat = est / se
            p = 2.0 * t_sf(abs(t_stat), dof)
        else:
            t_stat, p = 0.0, 1.0
        out[name] = {"estimate": est, "se": se, "t": t_stat, "p": p}
    out["n_pre"], out["n_post"] = n_pre, n_post
    out["dof"] = dof  # honest readout: the t-tests' degrees of freedom
    out["caveat"] = (
        "interrupted time series — association only; "
        "no concurrent control, seasonality not modeled"
    )
    return out


def _hist_value_at_rank(entries: list[tuple[int, int]], rank: float) -> float | None:
    """Value at a (possibly fractional) 1-based rank in a base-2 log
    histogram: walk cumulative counts, geometric interpolation between the
    bucket's bounds by the within-bucket rank fraction."""
    total = sum(c for _, c in entries)
    if total <= 0:
        return None
    rank = min(max(rank, 1.0), float(total))
    seen = 0
    for bucket, count in entries:
        if seen + count >= rank:
            lo, hi = 2.0 ** bucket, 2.0 ** (bucket + 1)
            frac = (rank - seen) / count
            return lo * (hi / lo) ** frac
        seen += count
    return 2.0 ** (entries[-1][0] + 1)


def histogram_quantile(hist: dict, p: float) -> dict | None:
    """§4.14 (round 124): quantile estimate + distribution-free CI from a
    base-2 log histogram {bucket: count} with "__zero__"/"__neg__" overflow
    keys. Refuses (None) on empty data, p outside (0,1), or ANY negative
    values (log buckets are for positive-domain metrics — latency, cost).
    CI from order statistics: rank bounds np ± z*sqrt(np(1-p)), mapped back
    through the histogram — conservative, no normality assumed."""
    if not hist or not (0.0 < p < 1.0):
        return None
    if int(hist.get("__neg__", 0) or 0) > 0:
        return None
    zeros = int(hist.get("__zero__", 0) or 0)
    entries = sorted(
        (int(k), int(v))
        for k, v in hist.items()
        if k not in ("__zero__", "__neg__") and int(v) > 0
    )
    n = zeros + sum(c for _, c in entries)
    if n < 2:
        return None

    def at_rank(rank: float) -> float:
        rank = min(max(rank, 1.0), float(n))
        if rank <= zeros:
            return 0.0
        value = _hist_value_at_rank(entries, rank - zeros)
        return 0.0 if value is None else value

    target = p * n
    estimate = at_rank(target)
    z = 1.959963984540054
    half = z * math.sqrt(n * p * (1.0 - p))
    return {
        "estimate": estimate,
        "ci": [at_rank(target - half), at_rank(target + half)],
        "n": n,
        "caveat": "distribution-free order-statistic CI; log-bucket resolution",
    }


def quantile_comparison(
    control_hist: dict, treatment_hist: dict, p: float
) -> dict | None:
    """Control-vs-treatment quantile difference. The combined CI subtracts
    opposite CI ends (conservative — wider than an exact two-sample
    interval, never narrower). Never a decision basis on its own."""
    c = histogram_quantile(control_hist, p)
    t = histogram_quantile(treatment_hist, p)
    if c is None or t is None:
        return None
    return {
        "control": c["estimate"],
        "treatment": t["estimate"],
        "diff": t["estimate"] - c["estimate"],
        "ci": [t["ci"][0] - c["ci"][1], t["ci"][1] - c["ci"][0]],
        "n_control": c["n"],
        "n_treatment": t["n"],
        "caveat": c["caveat"],
    }


def msprt_always_valid_p(z: float, tau: float = 1.0) -> float:
    """Mixture SPRT always-valid p-value for a standardized statistic z with
    N(0, tau²) mixture prior. Peek freely: p is valid at every look."""
    if tau <= 0:
        raise ValueError("tau must be > 0")
    t2 = tau * tau
    log_lr = 0.5 * math.log(1.0 / (1.0 + t2)) + z * z * t2 / (2.0 * (1.0 + t2))
    return min(1.0, math.exp(-log_lr))


def required_n_per_arm(
    baseline_rate: float, mde_rel: float, *, alpha: float = 0.05, power: float = 0.8
) -> int | None:
    """Two-proportion sample size per arm (design-time power, §4.13 v3):
    classic normal approximation with pooled variance under H0 and unpooled
    under H1. mde is a RELATIVE lift on the baseline (the industry
    convention). None for degenerate inputs (no detectable difference, or a
    lifted rate outside (0,1))."""
    p1 = baseline_rate
    p2 = p1 * (1.0 + mde_rel)
    if not (0.0 < p1 < 1.0) or not (0.0 < p2 < 1.0) or p1 == p2:
        return None
    z_a = norm_ppf(1.0 - alpha / 2.0)
    z_b = norm_ppf(power)
    pbar = (p1 + p2) / 2.0
    numerator = (
        z_a * math.sqrt(2.0 * pbar * (1.0 - pbar))
        + z_b * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2))
    ) ** 2
    return math.ceil(numerator / (p1 - p2) ** 2)


def obrien_fleming_boundary(look: int, max_looks: int, alpha: float = 0.05) -> float:
    """Classic OF approximation: z-boundary at look k of K is
    z_{alpha/2}·sqrt(K/k) — very conservative early, nominal at the end."""
    if not 1 <= look <= max_looks:
        raise ValueError("look must be in [1, max_looks]")
    return norm_ppf(1.0 - alpha / 2.0) * math.sqrt(max_looks / look)


# ── Multiplicity: Benjamini-Hochberg ─────────────────────────────────


def benjamini_hochberg(p_values: dict[str, float], q: float = 0.05) -> dict[str, bool]:
    """FDR control: returns {key: passes_fdr}. Standard step-up procedure."""
    if not p_values:
        return {}
    items = sorted(p_values.items(), key=lambda kv: kv[1])
    m = len(items)
    cutoff_rank = 0
    for rank, (_key, p) in enumerate(items, start=1):
        if p <= rank / m * q:
            cutoff_rank = rank
    return {key: rank <= cutoff_rank for rank, (key, _p) in enumerate(items, start=1)}


# ── Bayesian engine (§10 v2) ─────────────────────────────────────────


def bayes_binary(
    control_successes: float, control_n: float,
    treatment_successes: float, treatment_n: float,
    prior: tuple[float, float] = (1.0, 1.0),
    grid_points: int = 2001,
) -> dict:
    """Beta-Binomial posteriors. P(treatment beats control) by numeric
    integration ∫ f_t(x)·F_c(x) dx; credible interval on the difference via
    normal approximation of the posteriors (documented approximation)."""
    if control_n <= 0 or treatment_n <= 0:
        return {"insufficient_data": True}
    a1 = prior[0] + control_successes
    b1 = prior[1] + control_n - control_successes
    a2 = prior[0] + treatment_successes
    b2 = prior[1] + treatment_n - treatment_successes
    ln_beta2 = math.lgamma(a2) + math.lgamma(b2) - math.lgamma(a2 + b2)
    p_beat = 0.0
    step = 1.0 / (grid_points - 1)
    for i in range(1, grid_points - 1):
        x = i * step
        pdf2 = math.exp((a2 - 1.0) * math.log(x) + (b2 - 1.0) * math.log(1.0 - x) - ln_beta2)
        p_beat += pdf2 * betainc(a1, b1, x)
    p_beat *= step
    m1, m2 = a1 / (a1 + b1), a2 / (a2 + b2)
    v1 = a1 * b1 / ((a1 + b1) ** 2 * (a1 + b1 + 1.0))
    v2 = a2 * b2 / ((a2 + b2) ** 2 * (a2 + b2 + 1.0))
    se = math.sqrt(v1 + v2)
    diff = m2 - m1
    # Expected loss of shipping treatment ≈ E[max(p1-p2, 0)] (normal approx)
    z0 = diff / se if se > 0 else 0.0
    expected_loss = se * math.exp(-z0 * z0 / 2.0) / math.sqrt(2 * math.pi) - diff * norm_sf(z0)
    return {
        "p_beat_control": min(1.0, max(0.0, p_beat)),
        "expected_loss": max(0.0, expected_loss),
        "effect": diff,
        "credible_interval": [diff - Z_975 * se, diff + Z_975 * se],
        "control": {"posterior_mean": m1, "ci": [beta_ppf(0.025, a1, b1), beta_ppf(0.975, a1, b1)]},
        "treatment": {"posterior_mean": m2, "ci": [beta_ppf(0.025, a2, b2), beta_ppf(0.975, a2, b2)]},
    }


def bayes_continuous(
    n1: float, sum1: float, sumsq1: float,
    n2: float, sum2: float, sumsq2: float,
) -> dict:
    """Normal-approximation posterior over the mean difference (documented:
    a full NIG posterior is a v-next refinement; for n ≥ ~20 the normal
    approximation is standard practice)."""
    base = welch_from_stats(n1, sum1, sumsq1, n2, sum2, sumsq2)
    if base.get("insufficient_data"):
        return {"insufficient_data": True}
    m1, v1, nn1 = base["control"]["mean"], base["control"]["var"], base["control"]["n"]
    m2, v2, nn2 = base["treatment"]["mean"], base["treatment"]["var"], base["treatment"]["n"]
    se = math.sqrt(v1 / nn1 + v2 / nn2) if (v1 / nn1 + v2 / nn2) > 0 else 0.0
    diff = m2 - m1
    if se == 0:
        p_beat = 1.0 if diff > 0 else (0.0 if diff < 0 else 0.5)
        return {"p_beat_control": p_beat, "expected_loss": 0.0, "effect": diff,
                "credible_interval": [diff, diff]}
    z0 = diff / se
    expected_loss = se * math.exp(-z0 * z0 / 2.0) / math.sqrt(2 * math.pi) - diff * norm_sf(z0)
    return {
        "p_beat_control": norm_cdf(z0),
        "expected_loss": max(0.0, expected_loss),
        "effect": diff,
        "credible_interval": [diff - Z_975 * se, diff + Z_975 * se],
    }
