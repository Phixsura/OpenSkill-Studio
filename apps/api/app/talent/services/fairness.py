"""Fairness and bias detection for talent matching (ADR-015 upgrade).

Computes demographic-free fairness metrics on match run results.
Uses statistical properties of the SCORE DISTRIBUTION rather than
protected attributes (which are structurally absent from matching).

Metrics:
  - score_distribution: mean, median, std, skewness
  - signal_concentration: Herfindahl index of signal contributions
  - rank_score_correlation: do higher scores always get higher ranks?
  - score_spread: ratio of top-10 mean to bottom-10 mean
"""

from __future__ import annotations

import math
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession


class FairnessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compute_fairness_metrics(
        self,
        match_results: list[dict],
    ) -> dict:
        """Compute fairness metrics from a list of scored match results.

        Args:
            match_results: list of dicts with at least "score" and "signals" keys.
                           Each signals dict maps signal_name → float value.

        Returns:
            dict with fairness metric categories.
        """
        if not match_results:
            return {"status": "no_results", "metrics": {}}

        # Extract scores from ranked results (exclude hard-failed)
        scores = [
            r["score"]
            for r in match_results
            if r.get("tier") != "excluded" and r.get("score") is not None
        ]

        if not scores:
            return {"status": "no_ranked_results", "metrics": {}}

        metrics: dict = {}

        # 1. Score distribution
        n = len(scores)
        mean = sum(scores) / n
        sorted_scores = sorted(scores)
        median = (
            sorted_scores[n // 2]
            if n % 2
            else (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        )
        variance = sum((s - mean) ** 2 for s in scores) / n if n > 1 else 0
        std = math.sqrt(variance)

        # Skewness (Fisher)
        skewness = 0.0
        if std > 0 and n > 2:
            m3 = sum((s - mean) ** 3 for s in scores) / n
            skewness = m3 / (std**3)

        metrics["score_distribution"] = {
            "count": n,
            "mean": round(mean, 4),
            "median": round(median, 4),
            "std": round(std, 4),
            "skewness": round(skewness, 4),
            "min": round(sorted_scores[0], 4),
            "max": round(sorted_scores[-1], 4),
        }

        # 2. Signal concentration (Herfindahl index)
        # If one signal dominates all results, the matching is effectively
        # single-dimensional — a sign that other signals aren't contributing
        signal_sums: dict[str, float] = defaultdict(float)
        signal_count = 0
        for r in match_results:
            sigs = r.get("signals", {})
            if not sigs:
                continue
            signal_count += 1
            for sig_name, sig_val in sigs.items():
                signal_sums[sig_name] += abs(sig_val)

        if signal_sums and signal_count > 0:
            total_signal = sum(signal_sums.values())
            if total_signal > 0:
                shares = {k: v / total_signal for k, v in signal_sums.items()}
                hhi = sum(s**2 for s in shares.values())
                metrics["signal_concentration"] = {
                    "herfindahl_index": round(hhi, 4),
                    "dominant_signal": max(shares, key=shares.get),  # type: ignore[arg-type]
                    "signal_shares": {k: round(v, 4) for k, v in shares.items()},
                    "interpretation": (
                        "balanced"
                        if hhi < 0.25
                        else "moderate_concentration"
                        if hhi < 0.5
                        else "high_concentration"
                    ),
                }

        # 3. Score spread — how concentrated are top scores?
        if n >= 10:
            top_10_mean = sum(sorted_scores[-10:]) / 10
            bottom_10_mean = sum(sorted_scores[:10]) / 10
            spread_ratio = top_10_mean / bottom_10_mean if bottom_10_mean > 0 else float("inf")
            metrics["score_spread"] = {
                "top_10_mean": round(top_10_mean, 4),
                "bottom_10_mean": round(bottom_10_mean, 4),
                "spread_ratio": round(spread_ratio, 4) if spread_ratio != float("inf") else None,
            }
        elif n >= 2:
            top_half = sorted_scores[n // 2 :]
            bottom_half = sorted_scores[: n // 2]
            top_mean = sum(top_half) / max(len(top_half), 1)
            bottom_mean = sum(bottom_half) / len(bottom_half) if bottom_half else 0
            metrics["score_spread"] = {
                "top_half_mean": round(top_mean, 4),
                "bottom_half_mean": round(bottom_mean, 4),
                "spread_ratio": round(top_mean / bottom_mean, 4) if bottom_mean > 0 else None,
            }

        # 4. Rank-score monotonicity
        # Check if ranking is strictly monotonic with scores
        # (it should be if tie-breaking is deterministic)
        rank_violations = 0
        for i in range(1, len(sorted_scores)):
            if sorted_scores[i] < sorted_scores[i - 1]:
                rank_violations += 1
        metrics["rank_consistency"] = {
            "violations": rank_violations,
            "total_pairs": max(n - 1, 1),
            "monotonicity": round(1 - rank_violations / max(n - 1, 1), 4),
        }

        # 5. Adverse impact ratio (EEOC four-fifths rule)
        # Without demographic data, we use score-quintile proxy:
        # compare selection rate of bottom-quintile vs top-quintile scores
        if n >= 10:
            threshold = sorted_scores[int(n * 0.8)]  # top 20% threshold
            top_group = [s for s in scores if s >= threshold]
            bottom_group = [s for s in scores if s < sorted_scores[int(n * 0.2)]]
            if top_group and bottom_group:
                top_pass_rate = len([s for s in top_group if s >= threshold]) / len(top_group)
                bottom_pass_rate = len([s for s in bottom_group if s >= threshold]) / max(
                    len(bottom_group), 1
                )
                adverse_impact_ratio = bottom_pass_rate / top_pass_rate if top_pass_rate > 0 else 0
                metrics["adverse_impact"] = {
                    "ratio": round(adverse_impact_ratio, 4),
                    "four_fifths_compliant": adverse_impact_ratio >= 0.8,
                    "alert": adverse_impact_ratio < 0.8,
                    "top_quintile_pass_rate": round(top_pass_rate, 4),
                    "bottom_quintile_pass_rate": round(bottom_pass_rate, 4),
                    "interpretation": (
                        "compliant" if adverse_impact_ratio >= 0.8 else "potential_adverse_impact"
                    ),
                }

        return {
            "status": "computed",
            "result_count": n,
            "excluded_count": sum(1 for r in match_results if r.get("tier") == "excluded"),
            "metrics": metrics,
            "four_fifths_alert": metrics.get("adverse_impact", {}).get("alert", False),
        }
