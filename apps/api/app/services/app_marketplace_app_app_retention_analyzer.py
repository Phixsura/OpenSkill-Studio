"""App retention analyzer — analyze user retention cohorts."""


def analyze_retention(*, cohorts: list[dict]) -> dict:
    results = []
    for cohort in cohorts:
        initial = cohort.get("initial_users", 0)
        retained = cohort.get("retained_users", [])
        rates = [round(r / max(initial, 1) * 100, 1) for r in retained]
        results.append({
            "period": cohort["period"],
            "initial_users": initial,
            "retention_rates": rates,
            "day_30": rates[3] if len(rates) > 3 else None,
            "day_90": rates[6] if len(rates) > 6 else None,
        })
    avg_d30 = [r["day_30"] for r in results if r["day_30"] is not None]
    avg_d90 = [r["day_90"] for r in results if r["day_90"] is not None]
    return {
        "cohorts": results,
        "total_cohorts": len(results),
        "avg_day_30": round(sum(avg_d30) / max(len(avg_d30), 1), 1) if avg_d30 else None,
        "avg_day_90": round(sum(avg_d90) / max(len(avg_d90), 1), 1) if avg_d90 else None,
    }
