"""Canary Analysis — statistical comparison of canary vs baseline metrics.

Implements:
- Two-sample proportion test for error rates (z-test approximation)
- Latency comparison with percentile analysis
- Automatic pass/fail decision with configurable thresholds
- Multi-metric scoring with weighted aggregate
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math
import statistics


@dataclass
class MetricSample:
    name: str
    values: list[float] = field(default_factory=list)

    @property
    def mean(self) -> float:
        return statistics.mean(self.values) if self.values else 0

    @property
    def p50(self) -> float:
        return self._percentile(50)

    @property
    def p99(self) -> float:
        return self._percentile(99)

    def _percentile(self, pct: int) -> float:
        if not self.values: return 0
        s = sorted(self.values)
        idx = int(len(s) * pct / 100)
        return s[min(idx, len(s) - 1)]


@dataclass
class CanaryJudgment:
    metric: str
    baseline_value: float
    canary_value: float
    verdict: str  # pass, fail, inconclusive
    reason: str
    significance: float = 0.0  # z-score or effect size


class CanaryAnalysisService:
    def __init__(self):
        self._thresholds = {
            "error_rate": 0.01,     # canary error rate must not exceed baseline + 1%
            "latency_p50": 1.1,     # canary p50 must be within 110% of baseline
            "latency_p99": 1.2,     # canary p99 must be within 120% of baseline
        }

    def set_threshold(self, metric: str, value: float) -> None:
        self._thresholds[metric] = value

    def compare_error_rates(self, baseline_errors: int, baseline_total: int,
                            canary_errors: int, canary_total: int) -> CanaryJudgment:
        """Two-proportion z-test for error rate comparison."""
        if baseline_total == 0 or canary_total == 0:
            return CanaryJudgment("error_rate", 0, 0, "inconclusive",
                                  "Insufficient data")

        p_baseline = baseline_errors / baseline_total
        p_canary = canary_errors / canary_total

        # Pooled proportion
        p_pool = (baseline_errors + canary_errors) / (baseline_total + canary_total)

        if p_pool == 0 or p_pool == 1:
            verdict = "pass" if p_canary <= p_baseline else "fail"
            return CanaryJudgment("error_rate", p_baseline, p_canary, verdict,
                                  f"Baseline: {p_baseline:.4f}, Canary: {p_canary:.4f}")

        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/baseline_total + 1/canary_total))
        z_score = (p_canary - p_baseline) / se if se > 0 else 0

        threshold = self._thresholds.get("error_rate", 0.01)
        diff = p_canary - p_baseline

        if diff > threshold:
            verdict = "fail"
            reason = f"Error rate +{diff:.4f} exceeds threshold {threshold}"
        elif abs(z_score) < 1.96:  # 95% confidence
            verdict = "inconclusive"
            reason = f"Not statistically significant (z={z_score:.2f})"
        else:
            verdict = "pass"
            reason = f"Error rate within threshold (diff={diff:.4f})"

        return CanaryJudgment("error_rate", p_baseline, p_canary, verdict,
                              reason, significance=round(z_score, 3))

    def compare_latency(self, baseline: MetricSample,
                        canary: MetricSample) -> list[CanaryJudgment]:
        """Compare latency percentiles between baseline and canary."""
        judgments = []

        for pct_name, pct_fn, threshold_key in [
            ("p50", lambda s: s.p50, "latency_p50"),
            ("p99", lambda s: s.p99, "latency_p99"),
        ]:
            b_val = pct_fn(baseline)
            c_val = pct_fn(canary)

            if b_val == 0:
                judgments.append(CanaryJudgment(
                    f"latency_{pct_name}", b_val, c_val, "inconclusive",
                    "No baseline data"))
                continue

            ratio = c_val / b_val
            threshold = self._thresholds.get(threshold_key, 1.2)

            if ratio > threshold:
                verdict = "fail"
                reason = f"Canary {pct_name} {c_val:.1f}ms is {ratio:.2f}x baseline (threshold: {threshold}x)"
            else:
                verdict = "pass"
                reason = f"Canary {pct_name} within {threshold}x baseline ({ratio:.2f}x)"

            judgments.append(CanaryJudgment(
                f"latency_{pct_name}", b_val, c_val, verdict, reason,
                significance=round(ratio, 3)))

        return judgments

    def analyze(self, baseline_errors: int, baseline_total: int,
                canary_errors: int, canary_total: int,
                baseline_latency: list[float],
                canary_latency: list[float]) -> dict:
        """Full canary analysis with aggregate verdict."""
        error_judgment = self.compare_error_rates(
            baseline_errors, baseline_total, canary_errors, canary_total)

        baseline_sample = MetricSample("baseline", baseline_latency)
        canary_sample = MetricSample("canary", canary_latency)
        latency_judgments = self.compare_latency(baseline_sample, canary_sample)

        all_judgments = [error_judgment] + latency_judgments
        fails = [j for j in all_judgments if j.verdict == "fail"]
        inconclusive = [j for j in all_judgments if j.verdict == "inconclusive"]

        if fails:
            overall = "fail"
        elif len(inconclusive) == len(all_judgments):
            overall = "inconclusive"
        else:
            overall = "pass"

        return {
            "overall": overall,
            "judgments": [{"metric": j.metric, "verdict": j.verdict,
                           "reason": j.reason, "significance": j.significance}
                          for j in all_judgments],
            "fail_count": len(fails),
            "recommendation": "🔴 Roll back canary" if fails else
                              "🟡 Gather more data" if overall == "inconclusive" else
                              "🟢 Promote canary",
        }
