"""SLA monitor — track service level agreement compliance."""


def evaluate_sla(*, targets: dict, actuals: dict) -> dict:
    metrics = []
    for key, target in targets.items():
        actual = actuals.get(key, 0)
        lower_is_better = key in ("error_rate", "latency_p99", "latency_p95", "latency_p50")
        met = actual <= target if lower_is_better else actual >= target
        metrics.append({
            "metric": key, "target": target, "actual": actual,
            "met": met, "gap": round(actual - target, 3),
        })
    all_met = all(m["met"] for m in metrics)
    violated = [m["metric"] for m in metrics if not m["met"]]
    return {
        "compliant": all_met,
        "metrics": metrics,
        "violations": violated,
        "violation_count": len(violated),
        "overall_score": round(sum(1 for m in metrics if m["met"]) / max(len(metrics), 1) * 100, 1),
    }


def generate_sla_report(*, period: str, services: list[dict]) -> dict:
    results = []
    for svc in services:
        r = evaluate_sla(targets=svc["targets"], actuals=svc["actuals"])
        results.append({"service": svc["name"], **r})
    compliant_count = sum(1 for r in results if r["compliant"])
    return {
        "period": period,
        "services": results,
        "total_services": len(results),
        "compliant_services": compliant_count,
        "compliance_rate": round(compliant_count / max(len(results), 1) * 100, 1),
    }
