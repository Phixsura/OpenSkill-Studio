"""Statistical primitives for the Benchmark Lab and rollout guardrails.

World-class benchmarking (LMArena, Artificial Analysis, LaunchDarkly) rests on
proper statistics, not point estimates: Bradley-Terry MLE over pairwise human
preferences, confidence intervals on every reported dimension, and significance
tests before a rollout may call something a regression. Pure functions — no I/O.
"""

import math

# ── Normal distribution helpers ─────────────────────────────────────


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _two_sided_p(z: float) -> float:
    return max(min(2.0 * (1.0 - _norm_cdf(abs(z))), 1.0), 0.0)


# ── Descriptive stats with uncertainty ──────────────────────────────


def mean_std(values: list[float]) -> tuple[float, float, int]:
    """(mean, sample std, n). std=0 for n<2."""
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0
    mean = sum(values) / n
    if n < 2:
        return mean, 0.0, n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return mean, math.sqrt(var), n


def mean_ci95(values: list[float]) -> dict:
    """{"mean", "std", "n", "ci95": [lo, hi]} — normal approximation.

    AA reports ±CI on its Intelligence Index; every aggregated benchmark
    dimension here carries the same. For n<2 the CI degenerates to the point.
    """
    mean, std, n = mean_std(values)
    if n < 2:
        return {"mean": round(mean, 6), "std": 0.0, "n": n, "ci95": [round(mean, 6)] * 2}
    half = 1.96 * std / math.sqrt(n)
    return {
        "mean": round(mean, 6),
        "std": round(std, 6),
        "n": n,
        "ci95": [round(mean - half, 6), round(mean + half, 6)],
    }


def weighted_mean(pairs: list[tuple[float, float]]) -> float:
    """Mean of (value, weight) pairs; falls back to 0 on zero total weight."""
    total_w = sum(w for _, w in pairs)
    if total_w <= 0:
        return 0.0
    return sum(v * w for v, w in pairs) / total_w


# ── Significance tests (rollout comparison) ─────────────────────────


def welch_t_test(a: list[float], b: list[float]) -> dict:
    """Welch's unequal-variance t-test (normal approx for p; fine at n>=5).

    Returns {"p_value", "mean_a", "mean_b", "n_a", "n_b"}; p=1.0 when a side
    has <2 samples or both variances are zero with equal means.
    """
    mean_a, std_a, n_a = mean_std(a)
    mean_b, std_b, n_b = mean_std(b)
    out = {"mean_a": round(mean_a, 6), "mean_b": round(mean_b, 6), "n_a": n_a, "n_b": n_b}
    if n_a < 2 or n_b < 2:
        out["p_value"] = 1.0
        return out
    se_sq = (std_a**2) / n_a + (std_b**2) / n_b
    if se_sq == 0:
        out["p_value"] = 1.0 if mean_a == mean_b else 0.0
        return out
    t = (mean_a - mean_b) / math.sqrt(se_sq)
    out["p_value"] = round(_two_sided_p(t), 6)
    return out


def two_proportion_z_test(successes_a: int, n_a: int, successes_b: int, n_b: int) -> dict:
    """Two-proportion z-test (reliability comparisons)."""
    out = {
        "p_a": round(successes_a / n_a, 6) if n_a else 0.0,
        "p_b": round(successes_b / n_b, 6) if n_b else 0.0,
        "n_a": n_a,
        "n_b": n_b,
    }
    if n_a == 0 or n_b == 0:
        out["p_value"] = 1.0
        return out
    pooled = (successes_a + successes_b) / (n_a + n_b)
    se_sq = pooled * (1 - pooled) * (1 / n_a + 1 / n_b)
    if se_sq == 0:
        out["p_value"] = 1.0 if out["p_a"] == out["p_b"] else 0.0
        return out
    z = (out["p_a"] - out["p_b"]) / math.sqrt(se_sq)
    out["p_value"] = round(_two_sided_p(z), 6)
    return out


# ── Bradley-Terry MLE over pairwise preferences (LMArena/AA method) ──


def bradley_terry(
    wins: dict[tuple[str, str], float],
    *,
    iterations: int = 200,
    tol: float = 1e-9,
    elo_base: float = 1000.0,
    elo_scale: float = 400.0,
) -> dict[str, float]:
    """MLE Bradley-Terry strengths from pairwise win counts, reported as Elo.

    `wins[(a, b)]` = number of times a beat b (ties: add 0.5 to each side
    before calling). Uses the classic MM iteration with a +epsilon prior so
    undefeated/defeated items stay finite. Returns {item: elo} anchored so the
    mean Elo equals elo_base.
    """
    items: set[str] = set()
    for a, b in wins:
        items.add(a)
        items.add(b)
    if not items:
        return {}
    if len(items) == 1:
        return {next(iter(items)): elo_base}
    eps = 0.1  # prior pseudo-wins to regularize extremes
    w: dict[str, float] = dict.fromkeys(items, 0.0)  # total (regularized) wins
    pair_total: dict[tuple[str, str], float] = {}
    for (a, b), count in wins.items():
        key = (a, b) if a < b else (b, a)
        pair_total[key] = pair_total.get(key, 0.0) + count
    for (a, _b), count in wins.items():
        w[a] += count
    # Regularize: every ordered pair gets eps extra wins each way
    ordered_pairs = set(pair_total)
    for a, b in ordered_pairs:
        w[a] += eps
        w[b] += eps
        pair_total[(a, b)] += 2 * eps
    p = dict.fromkeys(items, 1.0)
    for _ in range(iterations):
        new_p: dict[str, float] = {}
        max_delta = 0.0
        for i in items:
            denom = 0.0
            for (a, b), total in pair_total.items():
                if i in (a, b):
                    denom += total / (p[a] + p[b])
            new_p[i] = (w[i] / denom) if denom > 0 else p[i]
        # Normalize (geometric mean = 1) for identifiability
        log_mean = sum(math.log(max(v, 1e-12)) for v in new_p.values()) / len(new_p)
        scale = math.exp(log_mean)
        for i in new_p:
            new_p[i] = max(new_p[i] / scale, 1e-12)
            max_delta = max(max_delta, abs(new_p[i] - p[i]))
        p = new_p
        if max_delta < tol:
            break
    return {
        item: round(elo_base + elo_scale * math.log10(strength), 2)
        for item, strength in p.items()
    }


def pairwise_wins_from_scores(
    rows: list[dict],
) -> dict[tuple[str, str], float]:
    """Derive pairwise wins from per-(context, judge) scores of competitors.

    rows: [{"context": case_id, "judge": reviewer_id, "item": run_id,
            "score": float}]. Within each (context, judge) group every item
    pair contributes one comparison; higher score wins, equal scores are a
    tie (0.5 each). This is how blind per-dimension scoring becomes
    Bradley-Terry input without asking reviewers to vote twice.
    """
    groups: dict[tuple, list[tuple[str, float]]] = {}
    for row in rows:
        groups.setdefault((row["context"], row["judge"]), []).append(
            (row["item"], float(row["score"]))
        )
    wins: dict[tuple[str, str], float] = {}
    for members in groups.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                (item_a, score_a), (item_b, score_b) = members[i], members[j]
                if item_a == item_b:
                    continue
                if score_a > score_b:
                    wins[(item_a, item_b)] = wins.get((item_a, item_b), 0.0) + 1.0
                elif score_b > score_a:
                    wins[(item_b, item_a)] = wins.get((item_b, item_a), 0.0) + 1.0
                else:  # tie → half win each way
                    wins[(item_a, item_b)] = wins.get((item_a, item_b), 0.0) + 0.5
                    wins[(item_b, item_a)] = wins.get((item_b, item_a), 0.0) + 0.5
    return wins


# ── Semver range matching (Renovate/deps.dev-grade constraints) ─────


def parse_version(value: str) -> tuple[int, int, int] | None:
    """Parse 'v1.2.3'/'1.2'/'2' → (major, minor, patch); None if unparseable."""
    if not isinstance(value, str):
        return None
    cleaned = value.strip().lstrip("vV")
    parts = cleaned.split("-")[0].split("+")[0].split(".")
    nums: list[int] = []
    for part in parts[:3]:
        if not part.isdigit():
            return None
        nums.append(int(part))
    if not nums:
        return None
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2])


def version_in_range(version: str, range_expr: str) -> bool | None:
    """Evaluate a version against a range like '>=2.0 <3.0', '^1.2', '~1.2.3',
    '==2.1.0' or a bare version prefix. Returns None when either side is
    unparseable — callers must treat None as 'cannot rule out' (fail open for
    impact analysis: unknown constraints still count as affected)."""
    v = parse_version(version)
    if v is None or not isinstance(range_expr, str) or not range_expr.strip():
        return None
    ok = True
    matched_any = False
    for token in range_expr.strip().split():
        matched_any = True
        if token.startswith(">="):
            bound = parse_version(token[2:])
            ok = ok and bound is not None and v >= bound
        elif token.startswith("<="):
            bound = parse_version(token[2:])
            ok = ok and bound is not None and v <= bound
        elif token.startswith(">"):
            bound = parse_version(token[1:])
            ok = ok and bound is not None and v > bound
        elif token.startswith("<"):
            bound = parse_version(token[1:])
            ok = ok and bound is not None and v < bound
        elif token.startswith("=="):
            bound = parse_version(token[2:])
            ok = ok and bound is not None and v == bound
        elif token.startswith("^"):
            bound = parse_version(token[1:])
            if bound is None:
                return None
            upper = (bound[0] + 1, 0, 0)
            ok = ok and bound <= v < upper
        elif token.startswith("~"):
            bound = parse_version(token[1:])
            if bound is None:
                return None
            upper = (bound[0], bound[1] + 1, 0)
            ok = ok and bound <= v < upper
        else:
            bound = parse_version(token)
            if bound is None:
                return None
            ok = ok and v == bound
        if not ok:
            return False
    return ok if matched_any else None
