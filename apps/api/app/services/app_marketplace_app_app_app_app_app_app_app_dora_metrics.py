"""DORA metrics calculator — calculate all four DORA metrics."""
from __future__ import annotations


def calculate_dora(deployments: list[dict], incidents: list[dict],
                   commits: list[dict], period_days: int = 30) -> dict:
    # Deployment Frequency
    deploy_freq = round(len(deployments) / max(period_days, 1), 2)
    freq_label = "elite" if deploy_freq >= 1 else ("high" if deploy_freq >= 1/7 else ("medium" if deploy_freq >= 1/30 else "low"))

    # Lead Time for Changes (commit to deploy)
    lead_times = [c.get("lead_time_hours", 0) for c in commits if c.get("lead_time_hours")]
    avg_lead = round(sum(lead_times) / max(len(lead_times), 1), 1) if lead_times else 0
    lead_label = "elite" if avg_lead < 1 else ("high" if avg_lead < 24 else ("medium" if avg_lead < 168 else "low"))

    # Change Failure Rate
    failed = sum(1 for d in deployments if d.get("caused_incident"))
    cfr = round(failed / max(len(deployments), 1) * 100, 1)
    cfr_label = "elite" if cfr < 5 else ("high" if cfr < 15 else ("medium" if cfr < 30 else "low"))

    # Mean Time to Recover
    recovery_times = [i.get("recovery_hours", 0) for i in incidents if i.get("recovery_hours")]
    mttr = round(sum(recovery_times) / max(len(recovery_times), 1), 1) if recovery_times else 0
    mttr_label = "elite" if mttr < 1 else ("high" if mttr < 24 else ("medium" if mttr < 168 else "low"))

    return {"deployment_frequency": {"value": deploy_freq, "label": freq_label},
            "lead_time": {"hours": avg_lead, "label": lead_label},
            "change_failure_rate": {"pct": cfr, "label": cfr_label},
            "mttr": {"hours": mttr, "label": mttr_label},
            "overall": _overall_level([freq_label, lead_label, cfr_label, mttr_label])}


def _overall_level(labels: list[str]) -> str:
    scores = {"elite": 4, "high": 3, "medium": 2, "low": 1}
    avg = sum(scores.get(l, 1) for l in labels) / len(labels)
    if avg >= 3.5: return "elite"
    if avg >= 2.5: return "high"
    if avg >= 1.5: return "medium"
    return "low"
